#!/usr/bin/env python3
"""Compila una aplicación con el producto SPM para dispositivo y simulador."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
TEMP = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'become-ios-spm-ci'

ADAPT_PROJECT = r'''
require 'xcodeproj'
project = Xcodeproj::Project.open(ARGV[0])
target = project.native_targets.find { |item| item.name == ARGV[1] }
raise 'No se encontró el target público' unless target
target.build_phases.each do |phase|
  next unless phase.respond_to?(:files)
  phase.files.to_a.each do |file|
    ref = file.file_ref
    if file.product_ref || (ref && File.basename(ref.path.to_s) == 'BDIdentityVerification.xcframework')
      file.remove_from_project
    end
  end
end
target.package_product_dependencies.to_a.each(&:remove_from_project)
project.root_object.package_references.to_a.each(&:remove_from_project)
reference = project.new(Xcodeproj::Project::Object::XCLocalSwiftPackageReference)
reference.relative_path = ARGV[2]
project.root_object.package_references << reference
product = project.new(Xcodeproj::Project::Object::XCSwiftPackageProductDependency)
product.package = reference
product.product_name = 'BDIdentityVerification'
target.package_product_dependencies << product
file = project.new(Xcodeproj::Project::Object::PBXBuildFile)
file.product_ref = product
target.frameworks_build_phase.files << file
project.save
'''


def invoke(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def prepare(root=ROOT, temporary=TEMP):
    config = json.loads((root / '.github/distribution.json').read_text())
    package = temporary / 'Package'
    package.mkdir(parents=True)
    manifest = (root / 'Package.swift').read_text()
    # El paquete conserva productos y dependencias; solo cambia la ubicación del binario.
    manifest, count = re.subn(r'url: artifactURL,\s*checksum: artifactChecksum',
                              'path: "BDIdentityVerification.xcframework"', manifest)
    if count != 1:
        raise ValueError('Se requiere un único target binario SPM.')
    (package / 'Package.swift').write_text(manifest)
    shutil.copytree(root / 'Sources', package / 'Sources')
    shutil.copytree(root / config['artifacts'][0], package / config['artifacts'][0])
    original = root / config['ios_project']
    app = temporary / 'App'
    shutil.copytree(original.parent, app, ignore=shutil.ignore_patterns(
        'build', 'DerivedData', '.build', 'xcuserdata', 'Secrets.plist', 'DemoConfiguration.plist'))
    project = app / original.name
    adapter = temporary / 'adaptar.rb'
    adapter.write_text(ADAPT_PROJECT)
    invoke('ruby', str(adapter), str(project), config['ios_scheme'], str(package))
    return project, config['ios_scheme']


def main():
    swift = subprocess.run(['swift','--version'], text=True, capture_output=True, check=True).stdout
    match = re.search(r'Swift version (\d+)\.(\d+)', swift)
    if not match or tuple(map(int,match.groups())) < (6,4):
        raise ValueError('El artefacto requiere Swift 6.4 o posterior.')
    manifest = (ROOT / 'Package.swift').read_text()
    version = re.search(r'^let artifactVersion = "([^"]+)"',manifest,re.MULTILINE).group(1)
    invoke('python3','scripts/prepare_spm_release.py','--version',version,'--check')
    project, scheme = prepare()
    common = ['-project',str(project),'-scheme',scheme,'-configuration','Release',
              '-derivedDataPath',str(TEMP/'DerivedData'),'-clonedSourcePackagesDirPath',str(TEMP/'Packages')]
    invoke('xcodebuild','-resolvePackageDependencies',*common)
    for destination, archs in [('generic/platform=iOS','arm64'),('generic/platform=iOS Simulator','arm64 x86_64')]:
        invoke('xcodebuild','build',*common,'-destination',destination,'ARCHS='+archs,
               '-onlyUsePackageVersionsFromResolvedFile','-disableAutomaticPackageResolution','-skipPackageUpdates',
               'CODE_SIGNING_ALLOWED=NO','ONLY_ACTIVE_ARCH=NO')


if __name__ == '__main__':
    main()
