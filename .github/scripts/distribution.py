#!/usr/bin/env python3
"""Validación y publicación de distribuciones binarias de Become Digital."""

from __future__ import annotations

import argparse
import importlib.util
import base64
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-rc\.([1-9]\d*))?\Z")
SECTIONS = {"agregado": "Novedades", "cambiado": "Cambios", "corregido": "Correcciones", "retirado": "Retiros"}


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def run(*args, cwd=None, data=None):
    result = subprocess.run(args, cwd=cwd or ROOT, input=data, text=True, capture_output=True)
    require(result.returncode == 0, f"Falló {args[0]}: {result.stderr[-3000:]}")
    return result.stdout.strip()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def version(value):
    match = VERSION.fullmatch(value)
    require(match, "La versión debe ser X.Y.Z o X.Y.Z-rc.N, sin ceros iniciales.")
    a, b, c, rc = match.groups()
    return (int(a), int(b), int(c), 1 if rc is None else 0, int(rc or 0))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def zip_bytes(files):
    """Empaqueta los mismos bytes de forma reproducible, sin modificar los binarios."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(files.items()):
            require(not name.startswith("/") and ".." not in Path(name).parts, "Ruta ZIP no permitida.")
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    return buffer.getvalue()


def files_under(root):
    root = Path(root)
    require(root.exists(), f"No existe {root.name}.")
    files = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), f"Enlace simbólico no permitido: {path.name}.")
        if path.is_file() and path.name != ".DS_Store":
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    require(files, "El artefacto está vacío.")
    return files


def inputs(config, root=ROOT):
    result = {}
    for name in config["artifacts"]:
        path = root / name
        require(path.exists() and not path.is_symlink(), f"Falta el artefacto {name}.")
        if path.is_dir():
            records = {key: digest(data) for key, data in files_under(path).items()}
            result[name] = digest(json.dumps(records, sort_keys=True, separators=(",", ":")).encode())
        else:
            result[name] = digest(path.read_bytes())
    return result


def release_inputs(config, root=ROOT):
    result = inputs(config, root)
    integration = {}
    for name in config.get('integration', []):
        text = (root / name).read_text(encoding='utf-8')
        if name == 'Package.swift':
            text = re.sub(r'^let artifact(?:Version|Checksum) = "[^"]+"$', '', text, flags=re.MULTILINE)
        integration[name] = digest(text.encode())
    result['integration_sha256'] = digest(json.dumps(integration, sort_keys=True).encode())
    return result


def macho(data):
    """Obtiene CPU y plataforma de cada slice Mach-O, incluidos binarios universales."""
    magic = bytes(data[:4])
    fat = {b"\xca\xfe\xba\xbe": (">", False), b"\xbe\xba\xfe\xca": ("<", False),
           b"\xca\xfe\xba\xbf": (">", True), b"\xbf\xba\xfe\xca": ("<", True)}
    if magic in fat:
        endian, wide = fat[magic]
        count = struct.unpack_from(endian + "I", data, 4)[0]
        require(0 < count <= 8, "Cabecera universal inválida.")
        result = {}
        for index in range(count):
            offset = 8 + index * (32 if wide else 20)
            start, size = struct.unpack_from(endian + ("QQ" if wide else "II"), data, offset + 8)
            require(start + size <= len(data), "Slice Mach-O truncada.")
            result.update(macho(data[start:start + size]))
        require(len(result) == count, "Arquitecturas duplicadas.")
        return result
    require(magic in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"), "Se esperaba Mach-O de 64 bits.")
    endian = "<" if magic == b"\xcf\xfa\xed\xfe" else ">"
    cpu = struct.unpack_from(endian + "I", data, 4)[0]
    name = {0x100000C: "arm64", 0x1000007: "x86_64"}.get(cpu)
    require(name, "Arquitectura iOS no reconocida.")
    ncmds = struct.unpack_from(endian + "I", data, 16)[0]
    offset, platform = 32, None
    for _ in range(ncmds):
        command, size = struct.unpack_from(endian + "II", data, offset)
        require(size >= 8 and offset + size <= len(data), "Comando Mach-O inválido.")
        if command == 0x32:
            platform = struct.unpack_from(endian + "I", data, offset + 8)[0]
        offset += size
    require(platform in (2, 7), "La slice no declara iOS o iOS Simulator.")
    return {name: platform}


def audit_ios(config, root=ROOT, publication=False):
    package = root / config["artifacts"][0]
    libraries = plistlib.loads((package / "Info.plist").read_bytes())["AvailableLibraries"]
    expected = {"device": {"arm64"}, "simulator": {"arm64", "x86_64"}}
    seen, apis, versions = set(), [], set()
    for library in libraries:
        require(library["SupportedPlatform"] == "ios", "Plataforma inesperada en el XCFramework.")
        kind = "simulator" if library.get("SupportedPlatformVariant") == "simulator" else "device"
        require(kind not in seen, "Plataforma duplicada en el XCFramework.")
        seen.add(kind)
        require(set(library["SupportedArchitectures"]) == expected[kind], f"Arquitecturas incompletas: {kind}.")
        framework = package / library["LibraryIdentifier"] / library["LibraryPath"]
        native = macho((framework / "BDIdentityVerification").read_bytes())
        require(set(native) == expected[kind] and set(native.values()) == {7 if kind == "simulator" else 2},
                f"El binario no corresponde a los metadatos: {kind}.")
        info = plistlib.loads((framework / "Info.plist").read_bytes())
        require(info.get("BaseUrl") == "https://api.svi.becomedigital.net", "El binario debe ser de producción.")
        versions.add(info["CFBundleShortVersionString"])
        for resource in config["resources"]:
            require((framework / resource).is_file(), f"Falta el recurso {resource}: {kind}.")
        if publication:
            privacy = framework / "PrivacyInfo.xcprivacy"
            require(privacy.is_file(), "Falta PrivacyInfo.xcprivacy en el framework distribuido.")
            plistlib.loads(privacy.read_bytes())
        for arch in sorted(expected[kind]):
            suffix = "-simulator" if kind == "simulator" else ""
            interface = framework / f"Modules/BDIdentityVerification.swiftmodule/{arch}-apple-ios{suffix}.swiftinterface"
            text = interface.read_text()
            require(all(symbol in text for symbol in config["public_api"]), "La API pública está incompleta.")
            require("import CaptureCore" in text and "import CaptureUX" in text and "import BlinkID" not in text,
                    "El artefacto no corresponde a la variante de esta distribución.")
            apis.append("\n".join(line.strip() for line in text.splitlines() if not line.startswith("//") and line.strip()))
    require(seen == set(expected), "Falta dispositivo o simulador en el XCFramework.")
    require(len(set(apis)) == 1, "La API pública difiere entre las slices.")
    require(len(versions) == 1, "Las versiones de las slices difieren.")
    return next(iter(versions))


def native_abis(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        native = {}
        for name in archive.namelist():
            parts = name.split("/")
            if len(parts) == 3 and parts[0] in ("jni", "lib") and name.endswith(".so"):
                binary = archive.read(name)
                require(binary[:4] == b"\x7fELF", f"Archivo ELF inválido: {name}.")
                machine = struct.unpack_from(("<" if binary[5] == 1 else ">") + "H", binary, 18)[0]
                require(machine == {"arm64-v8a": 183, "x86_64": 62, "armeabi-v7a": 40}.get(parts[1]),
                        f"La arquitectura real no corresponde al nombre: {name}.")
                native.setdefault(parts[1], set()).add(parts[2])
        return native


def audit_android(config, root=ROOT):
    failures = []
    declared_version = None
    for name in config["artifacts"]:
        data = (root / name).read_bytes()
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            require("classes.jar" in archive.namelist(), f"Falta classes.jar: {name}.")
            if name == "becomedigitalsdk.aar":
                require("proguard.txt" in archive.namelist(), "Faltan reglas R8 para la app consumidora.")
                with zipfile.ZipFile(io.BytesIO(archive.read("classes.jar"))) as classes:
                    class_names = classes.namelist()
                    for symbol in config["public_api"]:
                        require(any(path.endswith('/' + symbol + '.class') for path in class_names), f"Falta {symbol}.")
                    build_configs = [classes.read(path) for path in class_names if path.endswith('/BuildConfig.class')]
                    require(any(b"https://api.svi.becomedigital.net" in item for item in build_configs),
                            "No se pudo verificar el ambiente productivo del AAR.")
                    require(not any(b"api.dev.svi" in item for item in build_configs), "El AAR contiene configuración dev.")
                values = ET.fromstring(archive.read('res/values/values.xml'))
                sdk_version = values.find("string[@name='sdk_version']")
                declared = (sdk_version.text or '').strip('"\' ') if sdk_version is not None else ''
                declared_version = declared
                if not VERSION.fullmatch(declared):
                    failures.append('El AAR no declara una versión interna SemVer válida')
        abis = native_abis(data)
        require(abis or name not in config.get('native_artifacts', []), f'Faltan las bibliotecas nativas de {name}.')
        if abis:
            missing = {"arm64-v8a", "x86_64"} - set(abis)
            if missing:
                failures.append(f"{name}: faltan {', '.join(sorted(missing))}")
            for abi in ("arm64-v8a", "x86_64"):
                if abi in abis:
                    require(abis[abi] == abis.get("arm64-v8a", set()), f"Bibliotecas nativas distintas: {name} / {abi}.")
    require(not failures, "Soporte nativo incompleto; no se permite retirar ABIs para publicar. " + "; ".join(failures))
    return declared_version


def audit(config, root=ROOT, publication=False):
    module = platform_module(config, root)
    if config["platform"] == "ios":
        module.verify_existing_checksums()
        return audit_ios(config, root, publication)
    module.verify_checksums()
    return audit_android(config, root)


def notes(data):
    require(isinstance(data, dict) and set(data) == set(SECTIONS), "Categorías de notas inválidas.")
    lines = []
    forbidden = re.compile(r"(?i)(?:feature/|git (?:push|checkout)|github actions|pipeline|/Users/|api\.svi\.|amplify|\baws\b|\bsdk\b|microblink|blinkid|capture ?(?:core|ux)|https?://[^\s]+/actions/)")
    for key, title in SECTIONS.items():
        require(isinstance(data[key], list), "Cada categoría debe ser una lista.")
        if not data[key]:
            continue
        lines.extend([f"### {title}", ""])
        for item in data[key]:
            require(isinstance(item, str) and 10 <= len(item) <= 1000 and '\n' not in item and not forbidden.search(item),
                    "Las notas deben describir cambios públicos de integración en español, sin detalles internos.")
            lines.append(f"- {item}")
        lines.append("")
    require(lines, "Agrega al menos un cambio observable por la aplicación a las notas.")
    return "\n".join(lines).rstrip() + "\n"


def gh_json(*args, data=None):
    return json.loads(run("gh", "api", *args, *( ["--input", "-"] if data is not None else [] ), data=json.dumps(data) if data is not None else None))


def candidate(config, value, target_version, source_inputs, package_hashes=None):
    require(VERSION.fullmatch(value or "") and '-rc.' in value and value.split('-')[0] == target_version,
            "La versión final requiere una RC de la misma versión base.")
    release = gh_json(f"repos/{config['repository']}/releases/tags/{value}")
    require(release["prerelease"] and not release["draft"], "La RC debe estar publicada.")
    assets = [a for a in release["assets"] if a["name"] == "artefactos.json"]
    require(len(assets) == 1, "La RC no contiene el registro verificable de artefactos.")
    record = json.loads(run("gh", "api", f"repos/{config['repository']}/releases/assets/{assets[0]['id']}",
                            "-H", "Accept: application/octet-stream"))
    require(record["version"] == value and record["inputs"] == source_inputs,
            "Los binarios cambiaron desde la RC. Publica y valida una RC nueva.")
    if package_hashes is not None:
        require(record.get('payload_sha256') == package_hashes, 'El paquete difiere del validado en la RC.')


def platform_module(config, root=ROOT):
    name = "prepare_spm_release" if config["platform"] == "ios" else "prepare_maven_release"
    specification = importlib.util.spec_from_file_location(name, root / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def payload(config, value, root=ROOT):
    if config["platform"] == "ios":
        archive = platform_module(config, root).make_zip(value)
        return {archive.name: archive.read_bytes()}
    return {"BecomeDigital-Android-" + value + ".zip": zip_bytes({p: (root / p).read_bytes() for p in config["artifacts"]})}


def prepare(config, value, rc="", evidence=False, root=ROOT):
    parsed = version(value)
    tags = [tag for tag in run("git", "tag", "--list", cwd=root).splitlines() if VERSION.fullmatch(tag)]
    require(all(version(tag) < parsed for tag in tags), "La versión ya existe o no supera las versiones publicadas.")
    binary_version = audit(config, root, publication=True)
    if binary_version:
        require(binary_version == value.split('-')[0], "La versión base debe coincidir con la del artefacto recibido.")
    source_inputs = release_inputs(config, root)
    package_hashes = sorted(digest(data) for data in payload(config, value, root).values())
    if parsed[3] == 1:
        require(evidence is True, "Confirma la validación funcional de la RC antes de preparar la versión final.")
        candidate(config, rc, value, source_inputs, package_hashes)
    else:
        require(not rc and not evidence, "Una RC no debe declarar promoción de otra RC.")
    body = notes(load(root / ".github/notes.json"))
    current = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    require(f"## {value} " not in current, "La versión ya está en el changelog.")
    date = dt.datetime.now(dt.timezone.utc).date().isoformat()
    (root / "CHANGELOG.md").write_text(current.split('\n', 1)[0] + f"\n\n## {value} — {date}\n\n" + body + '\n' + current.split('\n', 1)[1].lstrip(), encoding="utf-8")
    record = {"version": value, "date": date, "candidate": rc, "functional_validation": evidence,
              "inputs": source_inputs, "payload_sha256": package_hashes, "notes_sha256": digest(body.encode())}
    save(root / ".github/release.json", record)
    if config["platform"] == "ios":
        archive = next(iter(payload(config, value, root).values()))
        platform_module(config, root).verify_or_update_manifest(value, digest(archive), False)
    return record


def release_record(config, value, root=ROOT):
    version(value)
    path = root / ".github/release.json"
    require(path.is_file(), "Primero prepara y revisa la versión mediante su pull request.")
    record = load(path)
    require(record["version"] == value, "La versión solicitada no coincide con la revisada.")
    require(record["inputs"] == release_inputs(config, root), "Cambió un binario o su integración después de preparar la versión.")
    package_hashes = sorted(digest(data) for data in payload(config, value, root).values())
    require(record.get('payload_sha256') == package_hashes, 'Cambió el paquete después de preparar la versión.')
    body = notes(load(root / ".github/notes.json"))
    require(record["notes_sha256"] == digest(body.encode()), "Cambiaron las notas después de preparar la versión.")
    changelog = (root / "CHANGELOG.md").read_text()
    require(f"## {value} — {record['date']}\n\n{body}" in changelog, "El changelog no corresponde a la versión.")
    binary_version = audit(config, root, publication=True)
    if binary_version:
        require(binary_version == value.split('-')[0], 'La versión interna no coincide exactamente con la versión base publicada.')
    if config["platform"] == "ios":
        checksum = digest(next(iter(payload(config, value, root).values())))
        platform_module(config, root).verify_or_update_manifest(value, checksum, True)
    else:
        platform_module(config, root).validate_artifacts(value.split('-')[0])
    if '-rc.' not in value:
        require(record.get("functional_validation") is True, "Falta la confirmación de validación funcional de la RC.")
        candidate(config, record["candidate"], value, record["inputs"], package_hashes)
    return record, body


def publication_gate(config):
    ref = os.environ.get("GITHUB_REF", "")
    require(ref == "refs/heads/main" or ref.startswith("refs/tags/"), "Solo main o un tag versionado pueden publicar.")
    run("git", "fetch", "origin", "main", "--tags")
    run("git", "merge-base", "--is-ancestor", "HEAD", "origin/main")
    environment = "maven-central" if config["platform"] == "android" else "sdk-release"
    settings = gh_json(f"repos/{config['repository']}/environments/{environment}")
    require(any(rule["type"] == "required_reviewers" and rule.get("reviewers") for rule in settings["protection_rules"]),
            f"Configura revisores obligatorios en el entorno {environment} antes de publicar.")
    require(not run("git", "status", "--porcelain", "--untracked-files=no"), "Hay cambios en archivos versionados.")


def optional_gh(endpoint):
    result = subprocess.run(['gh', 'api', endpoint], text=True, capture_output=True, cwd=ROOT)
    if result.returncode and '(HTTP 404)' in result.stderr:
        return None
    require(result.returncode == 0, 'No se pudo consultar GitHub; no se interpreta un fallo de acceso como ausencia de versión.')
    return json.loads(result.stdout)


def publish_github(config, value, output):
    record, _ = release_record(config, value)
    repository = config['repository']
    sha = run('git', 'rev-parse', 'HEAD')
    tag = optional_gh(f'repos/{repository}/git/ref/tags/{value}')
    if tag:
        target = tag['object']
        for _ in range(4):
            if target['type'] != 'tag':
                break
            target = gh_json(f"repos/{repository}/git/tags/{target['sha']}")['object']
        require(target['type'] == 'commit' and target['sha'] == sha, 'La etiqueta existente apunta a otro commit.')
    release = optional_gh(f'repos/{repository}/releases/tags/{value}')
    paths = [p for p in sorted(output.iterdir()) if p.is_file() and p.name not in ('central-deployment.json',)]
    require({'artefactos.json','SHA256SUMS','NOTAS.md'}.issubset(p.name for p in paths), 'El paquete de publicación está incompleto.')
    if release and not release['draft']:
        require(release['prerelease'] == ('-rc.' in value), 'El canal de la versión existente difiere.')
        require(tag, 'La publicación existente no tiene etiqueta verificable.')
    if not release:
        run('gh','release','create',value,'--repo',repository,'--draft','--target',sha,'--title',value,
            '--notes-file',str(output / 'NOTAS.md'))
        release = gh_json(f'repos/{repository}/releases/tags/{value}')
    assets = {asset['name']:asset for asset in release['assets']}
    require(set(assets).issubset(path.name for path in paths), 'El borrador contiene archivos no previstos; revísalo antes de continuar.')
    for path in paths:
        if path.name in assets:
            result = subprocess.run(['gh','api',f"repos/{repository}/releases/assets/{assets[path.name]['id']}",
                                     '-H','Accept: application/octet-stream'], capture_output=True, cwd=ROOT)
            require(result.returncode == 0 and digest(result.stdout) == digest(path.read_bytes()),
                    f'El archivo {path.name} ya existe con otros bytes. No se sobrescribe.')
        else:
            require(release['draft'], 'No se agregan archivos a una versión ya publicada.')
            run('gh','release','upload',value,str(path),'--repo',repository)
    if release['draft']:
        run('gh','release','edit',value,'--repo',repository,'--draft=false',
            '--prerelease=' + ('true' if '-rc.' in value else 'false'),
            '--latest=' + ('false' if '-rc.' in value else 'true'))


def verify_apk(config, path):
    packaged = native_abis(path.read_bytes())
    expected = set()
    for artifact in config['artifacts']:
        for libraries in native_abis((ROOT / artifact).read_bytes()).values():
            expected.update(libraries)
    for abi in ('arm64-v8a','x86_64'):
        require(expected.issubset(packaged.get(abi, set())), f'El APK no contiene todas las bibliotecas de {abi}.')


def maven_bundle(config, value, output, root=ROOT):
    module = platform_module(config, root)
    module.validate_artifacts(value.split('-')[0])
    license_url = os.environ.get("MAVEN_LICENSE_URL", "")
    require(license_url.startswith("https://") and "example.invalid" not in license_url,
            "Configura MAVEN_LICENSE_URL con los términos públicos aprobados.")
    license_name = os.environ.get('MAVEN_LICENSE_NAME', '').strip()
    require(license_name, 'Configura MAVEN_LICENSE_NAME con el nombre de la licencia aprobada.')
    module.stage(value, license_name, license_url, False, None)
    source = root / "dist/maven-repository"
    shutil.copytree(source, output / "maven", dirs_exist_ok=True)
    folders = [p.parent for p in (output / "maven").rglob("*.pom")]
    require(len(folders) == 1, "Debe existir una sola versión Maven preparada.")
    return folders[0]


def assemble(config, value, output):
    record, body = release_record(config, value)
    output.mkdir(parents=True, exist_ok=True)
    for name, data in payload(config, value).items():
        (output / name).write_bytes(data)
    save(output / 'artefactos.json', {"version":value,"inputs":record['inputs'],'payload_sha256':record['payload_sha256']})
    (output / 'NOTAS.md').write_text(f"## {value}\n\n" + ('Versión candidata para validar la integración.\n\n' if '-rc.' in value else '') + body, encoding='utf-8')
    if config['platform'] == 'android':
        maven_bundle(config, value, output)
    (output / 'SHA256SUMS').write_text(''.join(digest(p.read_bytes()) + '  ' + p.name + '\n' for p in sorted(output.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'))


def central_request(path, data=None, content_type=None):
    user, password = os.environ.get('MAVEN_CENTRAL_USERNAME'), os.environ.get('MAVEN_CENTRAL_PASSWORD')
    require(user and password, 'Faltan las credenciales de publicación de Sonatype.')
    token = base64.b64encode((user + ':' + password).encode()).decode()
    headers = {'Authorization':'Bearer ' + token}
    if content_type:
        headers['Content-Type'] = content_type
    request = urllib.request.Request('https://central.sonatype.com/api/v1/publisher/' + path, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise Invalid(f'Sonatype rechazó la operación: HTTP {exc.code}. Revisa el token y los metadatos.') from None


def publish_central(output):
    folders = [p.parent for p in (output / 'maven').rglob('*.pom')]
    require(len(folders) == 1, 'Debe existir una sola publicación Maven en el paquete.')
    folder = folders[0]
    for sidecar in list(folder.iterdir()):
        if sidecar.suffix in ('.md5','.sha1','.sha256','.sha512'):
            sidecar.unlink()
    # Un reintento después de publicar solo continúa si Central ya tiene exactamente esos bytes.
    for artifact in sorted(folder.glob('*.aar')):
        relative = artifact.relative_to(output / 'maven').as_posix()
        try:
            with urllib.request.urlopen('https://repo.maven.apache.org/maven2/' + relative, timeout=45) as response:
                require(digest(response.read()) == digest(artifact.read_bytes()), 'La versión Maven ya existe con otros bytes.')
            pom = artifact.with_suffix('.pom')
            with urllib.request.urlopen('https://repo.maven.apache.org/maven2/' + pom.relative_to(output / 'maven').as_posix(), timeout=45) as response:
                require(digest(response.read()) == digest(pom.read_bytes()), 'El POM publicado difiere; no se sobrescribe.')
            return
        except urllib.error.HTTPError as error:
            require(error.code == 404, f'No se pudo verificar la versión en Central: HTTP {error.code}.')
    require(os.environ.get('SIGNING_KEY') and os.environ.get('SIGNING_PASSWORD'), 'Falta la clave de firma o su contraseña.')
    with tempfile.TemporaryDirectory(prefix='become-signing-') as temporary:
        os.chmod(temporary, 0o700)
        # La clave y contraseña se entregan por stdin, nunca como argumentos o archivos versionados.
        run('gpg', '--homedir', temporary, '--batch', '--import', data=os.environ['SIGNING_KEY'])
        fingerprint = os.environ.get('SIGNING_FINGERPRINT', '').upper()
        require(re.fullmatch(r'[A-F0-9]{40,64}', fingerprint), 'Configura SIGNING_FINGERPRINT con la huella pública aprobada.')
        keys = run('gpg','--homedir',temporary,'--batch','--with-colons','--list-secret-keys')
        require(any(line.startswith('fpr:') and line.split(':')[9] == fingerprint for line in keys.splitlines()), 'La clave importada no corresponde a la huella aprobada.')
        for path in sorted(folder.iterdir()):
            run('gpg', '--homedir', temporary, '--batch', '--yes', '--pinentry-mode', 'loopback', '--passphrase-fd', '0',
                '--local-user', fingerprint, '--armor', '--detach-sign', '--output', str(path) + '.asc', str(path), data=os.environ['SIGNING_PASSWORD'] + '\n')
            run('gpg','--homedir',temporary,'--batch','--verify',str(path) + '.asc',str(path))
    for path in list(folder.iterdir()):
        for algorithm in ('md5', 'sha1', 'sha256'):
            path.with_name(path.name + '.' + algorithm).write_text(hashlib.new(algorithm, path.read_bytes()).hexdigest())
    bundle = zip_bytes({p.relative_to(output / 'maven').as_posix():p.read_bytes() for p in folder.iterdir()})
    boundary = 'BecomeCentralUpload'
    request = (f'--{boundary}\r\nContent-Disposition: form-data; name="bundle"; filename="bundle.zip"\r\nContent-Type: application/zip\r\n\r\n'.encode()
               + bundle + f'\r\n--{boundary}--\r\n'.encode())
    deployment = central_request('upload?publishingType=USER_MANAGED', request, 'multipart/form-data; boundary=' + boundary).decode().strip().strip('"')
    require(re.fullmatch(r'[A-Za-z0-9-]+', deployment), 'Identificador de despliegue inválido.')
    save(output / 'central-deployment.json', {'deployment_id':deployment})
    publish_requested = False
    for _ in range(120):
        status = json.loads(central_request('status?id=' + deployment, b''))
        state = status['deploymentState']
        if state == 'PUBLISHED':
            return
        require(state != 'FAILED', 'Sonatype no validó la publicación. Revisa el despliegue en Central Portal.')
        if state == 'VALIDATED' and not publish_requested:
            central_request('deployment/' + deployment, b'')
            publish_requested = True
        time.sleep(15)
    raise Invalid('La publicación sigue pendiente en Sonatype. Consulta el deployment_id antes de reintentar.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['check','prepare','preflight','assemble','publish-central','publish-github','verify-apk'])
    parser.add_argument('--version', default=os.environ.get('RELEASE_VERSION', ''))
    parser.add_argument('--candidate', default=os.environ.get('RELEASE_CANDIDATE', ''))
    parser.add_argument('--functional-verified', action='store_true', default=os.environ.get('FUNCTIONAL_VERIFIED') == 'true')
    parser.add_argument('--output', type=Path, default=Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'become-release')
    args = parser.parse_args()
    config = load(ROOT / '.github/distribution.json')
    if args.command == 'prepare' and os.environ.get('RELEASE_NOTES_JSON'):
        data = json.loads(os.environ['RELEASE_NOTES_JSON'])
        notes(data)
        save(ROOT / '.github/notes.json', data)
    if args.command == 'check':
        audit(config)
    elif args.command == 'prepare':
        prepare(config, args.version, args.candidate, args.functional_verified)
    elif args.command == 'preflight':
        publication_gate(config)
        release_record(config, args.version)
        tags = run('git','tag','--list').splitlines()
        require(not any(VERSION.fullmatch(tag) and version(tag) > version(args.version) for tag in tags),
                'Ya existe una versión posterior. No se publicará una versión anterior como la más reciente.')
        ref = os.environ['GITHUB_REF']
        require(not ref.startswith('refs/tags/') or ref == 'refs/tags/' + args.version, 'El tag no coincide con la versión preparada.')
    elif args.command == 'assemble':
        assemble(config, args.version, args.output)
    elif args.command == 'publish-central':
        publish_central(args.output)
    elif args.command == 'publish-github':
        publish_github(config, args.version, args.output)
    elif args.command == 'verify-apk':
        verify_apk(config, args.output)
    print('Validación completada.')


if __name__ == '__main__':
    try:
        main()
    except (Invalid, OSError, KeyError, ValueError, zipfile.BadZipFile, struct.error) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
