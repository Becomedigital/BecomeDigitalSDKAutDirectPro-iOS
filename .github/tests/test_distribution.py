"""Regresiones de seguridad, promoción y validación de artefactos de distribución."""

import importlib.util
import io
import json
import os
from pathlib import Path
import plistlib
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error


SPEC = importlib.util.spec_from_file_location('distribution', Path(__file__).resolve().parents[1] / 'scripts/distribution.py')
d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(d)


def thin(cpu, platform):
    return struct.pack('<8I', 0xFEEDFACF, cpu, 0, 6, 1, 24, 0, 0) + struct.pack('<6I', 0x32, 24, platform, 0, 0, 0)


def fat():
    arm, intel = thin(0x100000C, 7), thin(0x1000007, 7)
    return (struct.pack('>II', 0xCAFEBABE, 2) + struct.pack('>5I', 0x100000C, 0, 48, len(arm), 0)
            + struct.pack('>5I', 0x1000007, 0, 48 + len(arm), len(intel), 0) + arm + intel)


def elf(machine):
    data = bytearray(64)
    data[:6] = b'\x7fELF\x02\x01'
    struct.pack_into('<H', data, 18, machine)
    return bytes(data)


class Versions(unittest.TestCase):
    def test_final_sorts_after_its_candidates(self):
        self.assertLess(d.version('3.5.1-rc.2'), d.version('3.5.1-rc.10'))
        self.assertLess(d.version('3.5.1-rc.10'), d.version('3.5.1'))

    def test_rejects_unbounded_or_injected_versions(self):
        for value in ['01.2.3','1.2','1.2.3-rc.0','1.2.3-beta.1','v1.2.3','1.2.3; echo x','1.2.3\n','1.2.3+build','latest']:
            with self.subTest(value=value), self.assertRaises(d.Invalid):
                d.version(value)


class Artifacts(unittest.TestCase):
    def test_zip_is_reproducible_and_order_independent(self):
        self.assertEqual(d.zip_bytes({'b':b'2','a':b'1'}), d.zip_bytes({'a':b'1','b':b'2'}))

    def test_zip_rejects_escaping_paths(self):
        for path in ['/secret','../secret','a/../../secret']:
            with self.assertRaises(d.Invalid):
                d.zip_bytes({path:b'x'})

    def test_ios_checks_real_architectures_and_platform(self):
        self.assertEqual(d.macho(thin(0x100000C, 2)), {'arm64':2})
        self.assertEqual(d.macho(fat()), {'arm64':7,'x86_64':7})
        with self.assertRaises(d.Invalid):
            d.macho(thin(0x100000C, 1))

    def test_universal_binary_rejects_duplicate_or_truncated_slices(self):
        data = bytearray(fat())
        struct.pack_into('<I', data, 48 + 56 + 4, 0x100000C)
        with self.assertRaises(d.Invalid):
            d.macho(data)
        with self.assertRaises(d.Invalid):
            d.macho(fat()[:-20])

    def test_elf_architecture_must_match_abi_name(self):
        archive = d.zip_bytes({'jni/arm64-v8a/libCapture.so':elf(183), 'jni/x86_64/libCapture.so':elf(62)})
        self.assertEqual(set(d.native_abis(archive)), {'arm64-v8a','x86_64'})
        with self.assertRaises(d.Invalid):
            d.native_abis(d.zip_bytes({'jni/x86_64/libCapture.so':elf(183)}))

    def test_android_rejects_device_only_native_dependency(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'capture.aar').write_bytes(d.zip_bytes({'classes.jar':d.zip_bytes({'Type.class':b'class'}),
                                                       'jni/arm64-v8a/libCapture.so':elf(183)}))
            with self.assertRaisesRegex(d.Invalid,'x86_64'):
                d.audit_android({'artifacts':['capture.aar']},root)

    def test_symlink_cannot_escape_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'link').symlink_to('/etc/hosts')
            with self.assertRaises(d.Invalid):
                d.files_under(root)

    def test_locked_hash_changes_when_artifact_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root/'sdk.aar'
            path.write_bytes(b'first')
            before = d.inputs({'artifacts':['sdk.aar']},root)
            path.write_bytes(b'second')
            self.assertNotEqual(before, d.inputs({'artifacts':['sdk.aar']},root))

    def test_candidate_binds_integration_but_ignores_spm_version_assignment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'sdk.aar').write_bytes(b'artifact')
            manifest = root/'Package.swift'
            manifest.write_text('let artifactVersion = "1.2.3-rc.1"\nlet artifactChecksum = "123"\nexact: "1.4.3"\n')
            config = {'artifacts':['sdk.aar'],'integration':['Package.swift']}
            before = d.release_inputs(config,root)
            manifest.write_text('let artifactVersion = "1.2.3"\nlet artifactChecksum = "456"\nexact: "1.4.3"\n')
            self.assertEqual(before,d.release_inputs(config,root))
            manifest.write_text(manifest.read_text().replace('1.4.3','1.5.0'))
            self.assertNotEqual(before,d.release_inputs(config,root))


class NotesAndPromotion(unittest.TestCase):
    def customer_notes(self):
        return {'agregado':[],'cambiado':[],'corregido':['La aplicación conserva el resultado al volver a la pantalla.'],'retirado':[]}

    def test_notes_reject_empty_internal_and_multiline_entries(self):
        for text in ['', 'Cambio de pipeline interno', 'Cambios en feature/test', 'Actualizar Microblink a otra versión', 'Texto público\n## Encabezado inyectado']:
            data = self.customer_notes()
            data['corregido'] = [text]
            with self.assertRaises(d.Invalid):
                d.notes(data)
        self.assertIn('### Correcciones',d.notes(self.customer_notes()))

    def test_release_manifest_detects_tampered_binary_or_notes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = {'platform':'android','artifacts':['sdk.aar']}
            (root/'sdk.aar').write_bytes(b'candidate')
            (root/'CHANGELOG.md').write_text('# Historial de versiones\n')
            d.save(root/'.github/notes.json',self.customer_notes())
            with patch.object(d,'run',return_value=''), patch.object(d,'audit',return_value=None), patch.object(d,'platform_module'):
                d.prepare(config,'3.5.1-rc.1',root=root)
                d.release_record(config,'3.5.1-rc.1',root=root)
                (root/'sdk.aar').write_bytes(b'other')
                with self.assertRaisesRegex(d.Invalid,'Cambió un binario'):
                    d.release_record(config,'3.5.1-rc.1',root=root)
                (root/'sdk.aar').write_bytes(b'candidate')
                data=self.customer_notes(); data['agregado']=['Se admite una configuración adicional de la aplicación.']
                d.save(root/'.github/notes.json',data)
                with self.assertRaisesRegex(d.Invalid,'Cambiaron las notas'):
                    d.release_record(config,'3.5.1-rc.1',root=root)

    def test_rejects_reusing_or_regressing_a_version(self):
        with patch.object(d,'run',return_value='3.5.1-rc.2'):
            for value in ['3.5.1-rc.2','3.5.1-rc.1','3.4.9']:
                with self.assertRaisesRegex(d.Invalid,'versión ya existe'):
                    d.prepare({},value)

    def test_final_requires_same_version_published_rc_and_same_inputs(self):
        config={'repository':'organization/project'}
        release={'prerelease':True,'draft':False,'assets':[{'name':'artefactos.json','id':42}]}
        with patch.object(d,'gh_json',return_value=release), patch.object(d,'run',return_value=json.dumps({'version':'3.5.1-rc.1','inputs':{'sdk':'abc'}})):
            d.candidate(config,'3.5.1-rc.1','3.5.1',{'sdk':'abc'})
            with self.assertRaisesRegex(d.Invalid,'binarios cambiaron'):
                d.candidate(config,'3.5.1-rc.1','3.5.1',{'sdk':'changed'})
            with self.assertRaises(d.Invalid):
                d.candidate(config,'3.5.0-rc.1','3.5.1',{'sdk':'abc'})
        release['draft']=True
        with patch.object(d,'gh_json',return_value=release), self.assertRaisesRegex(d.Invalid,'RC debe estar publicada'):
            d.candidate(config,'3.5.1-rc.1','3.5.1',{})

    def test_final_rejects_repacked_candidate_even_with_same_binary_hashes(self):
        release={'prerelease':True,'draft':False,'assets':[{'name':'artefactos.json','id':42}]}
        receipt={'version':'3.5.1-rc.1','inputs':{'sdk':'abc'},'payload_sha256':['original']}
        with patch.object(d,'gh_json',return_value=release), patch.object(d,'run',return_value=json.dumps(receipt)):
            with self.assertRaisesRegex(d.Invalid,'paquete difiere'):
                d.candidate({'repository':'o/r'},'3.5.1-rc.1','3.5.1',{'sdk':'abc'},['repacked'])

    def test_permission_failure_is_not_treated_as_missing_release(self):
        with patch.object(d.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','gh: forbidden (HTTP 403)')):
            with self.assertRaises(d.Invalid): d.optional_gh('repos/o/r/releases/tags/1.2.3')
        with patch.object(d.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','gh: not found (HTTP 404)')):
            self.assertIsNone(d.optional_gh('repos/o/r/releases/tags/1.2.3'))

    def test_release_ref_must_be_main_or_a_tag(self):
        for ref in ['refs/heads/feature/test','refs/pull/1/merge','']:
            with patch.dict(os.environ,{'GITHUB_REF':ref}), self.assertRaises(d.Invalid):
                d.publication_gate({'platform':'ios'})

    def test_environment_without_approval_blocks_publication(self):
        with patch.dict(os.environ,{'GITHUB_REF':'refs/heads/main'}), patch.object(d,'run',return_value=''), patch.object(d,'gh_json',return_value={'protection_rules':[]}):
            with self.assertRaisesRegex(d.Invalid,'revisores obligatorios'):
                d.publication_gate({'platform':'android','repository':'o/r'})

    def test_central_does_not_echo_response_or_credentials_on_http_error(self):
        error=urllib.error.HTTPError('https://central.sonatype.com',401,'secret-value',{},None)
        with patch.dict(os.environ,{'MAVEN_CENTRAL_USERNAME':'private-user','MAVEN_CENTRAL_PASSWORD':'private-password'}), patch.object(d.urllib.request,'urlopen',side_effect=error):
            with self.assertRaises(d.Invalid) as caught: d.central_request('status',b'')
            self.assertNotIn('private',str(caught.exception))
            self.assertNotIn('secret-value',str(caught.exception))


class IOSPackage(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.config={'artifacts':['SDK.xcframework'],'resources':['Assets.car'],'public_api':['BDIVConfig']}
        self.frameworks=[]
        libraries=[]
        for kind, archs, binary in [('device',['arm64'],thin(0x100000C,2)),('simulator',['arm64','x86_64'],fat())]:
            item={'SupportedPlatform':'ios','LibraryIdentifier':kind,'LibraryPath':'BDIdentityVerification.framework','SupportedArchitectures':archs}
            if kind=='simulator': item['SupportedPlatformVariant']='simulator'
            libraries.append(item)
            bundle=self.root/'SDK.xcframework'/kind/'BDIdentityVerification.framework'
            module=bundle/'Modules/BDIdentityVerification.swiftmodule'
            module.mkdir(parents=True)
            (bundle/'BDIdentityVerification').write_bytes(binary)
            (bundle/'Assets.car').write_bytes(b'resource')
            (bundle/'Info.plist').write_bytes(plistlib.dumps({'CFBundleShortVersionString':'3.5.1','BaseUrl':'https://api.svi.becomedigital.net'}))
            for arch in archs:
                suffix='-simulator' if kind=='simulator' else ''
                (module/f'{arch}-apple-ios{suffix}.swiftinterface').write_text('// target específico\nimport CaptureCore\nimport CaptureUX\npublic struct BDIVConfig {}\n')
            self.frameworks.append(bundle)
        (self.root/'SDK.xcframework/Info.plist').write_bytes(plistlib.dumps({'AvailableLibraries':libraries}))

    def test_valid_device_and_universal_simulator(self):
        self.assertEqual(d.audit_ios(self.config,self.root),'3.5.1')

    def test_rejects_wrong_platform_despite_correct_architecture(self):
        (self.frameworks[0]/'BDIdentityVerification').write_bytes(thin(0x100000C,7))
        with self.assertRaisesRegex(d.Invalid,'metadatos'):
            d.audit_ios(self.config,self.root)

    def test_rejects_public_api_differences_between_architectures(self):
        interface=self.frameworks[1]/'Modules/BDIdentityVerification.swiftmodule/x86_64-apple-ios-simulator.swiftinterface'
        interface.write_text(interface.read_text()+'public func soloIntel() {}\n')
        with self.assertRaisesRegex(d.Invalid,'API pública difiere'):
            d.audit_ios(self.config,self.root)

    def test_publication_requires_privacy_resources_in_every_slice(self):
        with self.assertRaisesRegex(d.Invalid,'PrivacyInfo'):
            d.audit_ios(self.config,self.root,True)
        for framework in self.frameworks:
            (framework/'PrivacyInfo.xcprivacy').write_bytes(plistlib.dumps({'NSPrivacyTracking':False}))
        self.assertEqual(d.audit_ios(self.config,self.root,True),'3.5.1')

    def test_missing_resource_blocks_packaging(self):
        (self.frameworks[1]/'Assets.car').unlink()
        with self.assertRaisesRegex(d.Invalid,'recurso'):
            d.audit_ios(self.config,self.root)


class Publication(unittest.TestCase):
    def test_existing_github_asset_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            for name in ['NOTAS.md','SHA256SUMS','artefactos.json']:
                (output/name).write_bytes(b'approved')
            tag={'object':{'type':'commit','sha':'abc'}}
            release={'draft':False,'prerelease':True,'assets':[{'name':name,'id':i} for i,name in enumerate(['NOTAS.md','SHA256SUMS','artefactos.json'])]}
            with patch.object(d,'release_record',return_value=({},'')), patch.object(d,'run',return_value='abc') as run, patch.object(d,'optional_gh',side_effect=[tag,release]), patch.object(d.subprocess,'run',return_value=subprocess.CompletedProcess([],0,b'other',b'')):
                with self.assertRaisesRegex(d.Invalid,'No se sobrescribe'):
                    d.publish_github({'repository':'o/r'},'3.5.1-rc.1',output)
                self.assertEqual(run.call_count,1)

    def test_central_signs_payload_only_and_waits_for_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            folder=output/'maven/net/becomedigital/sdk/3.5.1'
            folder.mkdir(parents=True)
            (folder/'sdk-3.5.1.aar').write_bytes(b'aar')
            (folder/'sdk-3.5.1.pom').write_bytes(b'pom')
            (folder/'sdk-3.5.1.aar.sha256').write_text('old-checksum')
            fingerprint='A'*40
            signed=[]
            def process(*args,**kwargs):
                if '--list-secret-keys' in args:
                    return 'fpr:::::::::'+fingerprint+':'
                if '--detach-sign' in args:
                    signed.append(args[-1])
                    Path(args[args.index('--output')+1]).write_bytes(b'signature')
                return ''
            states=iter(['VALIDATING','VALIDATED','VALIDATED','PUBLISHING','PUBLISHED'])
            def request(path,*args):
                if path.startswith('upload?'): return b'deployment-123'
                if path.startswith('status?'): return json.dumps({'deploymentState':next(states)}).encode()
                return b''
            environment={'SIGNING_KEY':'private-key','SIGNING_PASSWORD':'passphrase','SIGNING_FINGERPRINT':fingerprint}
            missing=urllib.error.HTTPError('url',404,'not found',{},None)
            with patch.dict(os.environ,environment), patch.object(d,'run',side_effect=process), patch.object(d,'central_request',side_effect=request) as api, patch.object(d.urllib.request,'urlopen',side_effect=missing), patch.object(d.time,'sleep'):
                d.publish_central(output)
                self.assertEqual(len(signed),2)
                self.assertTrue(all(Path(path).suffix in ('.aar','.pom') for path in signed))
                self.assertEqual(sum(call.args[0]=='deployment/deployment-123' for call in api.call_args_list),1)
                self.assertEqual(d.load(output/'central-deployment.json')['deployment_id'],'deployment-123')


if __name__ == '__main__':
    unittest.main()
