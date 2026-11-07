#!/usr/bin/env python3
"""Valida y empaqueta el XCFramework para una versión SwiftPM."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = ROOT / "BDIdentityVerification.xcframework"
MANIFEST = ROOT / "Package.swift"
CHECKSUMS = ROOT / "CHECKSUMS.sha256"
RELEASE_BASE = "https://github.com/Becomedigital/BecomeDigitalSDKAutDirectPro-iOS/releases/download"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_existing_checksums() -> None:
    checked_paths: set[Path] = set()
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        expected, relative = line.split("  ", 1)
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(FRAMEWORK) or not path.is_file() or path in checked_paths:
            raise ValueError(f"Ruta de checksum ausente o insegura: {relative}")
        checked_paths.add(path)
        if sha256(path) != expected:
            raise ValueError(f"El XCFramework difiere de CHECKSUMS.sha256: {relative}")
    framework_paths = {path.resolve() for path in FRAMEWORK.rglob("*") if path.is_file()}
    if checked_paths != framework_paths:
        raise ValueError("CHECKSUMS.sha256 no cubre todos los archivos del XCFramework")


def inspect_framework(release_version: str, require_privacy_manifest: bool) -> None:
    with (FRAMEWORK / "Info.plist").open("rb") as stream:
        info = plistlib.load(stream)
    libraries = info.get("AvailableLibraries", [])
    if len(libraries) != 2:
        raise ValueError("Se requiere una variante de dispositivo y una de simulador iOS")

    expected_slices = {
        ("ios", None): {"arm64"},
        ("ios", "simulator"): {"arm64", "x86_64"},
    }
    seen: set[tuple[str, str | None]] = set()
    public_interfaces: list[str] = []
    for library in libraries:
        key = (library.get("SupportedPlatform"), library.get("SupportedPlatformVariant"))
        if key not in expected_slices or key in seen:
            raise ValueError(f"Variante XCFramework inesperada o duplicada: {key}")
        seen.add(key)
        if set(library.get("SupportedArchitectures", [])) != expected_slices[key]:
            raise ValueError(f"Arquitecturas inesperadas para {key}")

        bundle = FRAMEWORK / library["LibraryIdentifier"] / library["LibraryPath"]
        executable = bundle / "BDIdentityVerification"
        actual_architectures = set(subprocess.run(
            ["lipo", "-archs", str(executable)],
            check=True, text=True, capture_output=True,
        ).stdout.split())
        if actual_architectures != expected_slices[key]:
            raise ValueError(f"Las arquitecturas reales difieren de los metadatos: {bundle}")
        with (bundle / "Info.plist").open("rb") as stream:
            bundle_info = plistlib.load(stream)
        expected_bundle_version = release_version.split("-", 1)[0]
        if bundle_info.get("CFBundleShortVersionString") != expected_bundle_version:
            raise ValueError(f"La versión del framework difiere de {release_version}: {bundle}")
        if bundle_info.get("MinimumOSVersion") != "16.0":
            raise ValueError(f"Se requiere iOS 16.0 como mínimo en {bundle}")
        if bundle_info.get("BaseUrl") != "https://api.svi.becomedigital.net":
            raise ValueError(f"La URL de la API no corresponde a producción en {bundle}")

        required = (
            "BDIdentityVerification",
            "Assets.car",
            "Model.momd/Model.mom",
            "amplifyconfiguration.json",
            "AmplifyUILiveness_FaceLiveness.bundle/face_detection_short_range.mlmodelc/model.espresso.weights",
            "Fonts/Inter.ttf",
            "recording.gif",
            "es.lproj/Dictionary.stringsdict",
            "en.lproj/Dictionary.stringsdict",
        )
        for relative in required:
            if not (bundle / relative).is_file():
                raise ValueError(f"Falta un recurso requerido: {bundle / relative}")
        module = bundle / "Modules" / "BDIdentityVerification.swiftmodule"
        for architecture in sorted(expected_slices[key]):
            suffix = "-simulator" if key[1] == "simulator" else ""
            interface = module / f"{architecture}-apple-ios{suffix}.swiftinterface"
            contents = interface.read_text(encoding="utf-8")
            if "Apple Swift version 6.4" not in contents.splitlines()[1]:
                raise ValueError(f"Compilador Swift inesperado en {interface}")
            public_interfaces.append("\n".join(
                line for line in contents.splitlines()
                if not line.startswith("// swift-module-flags:")
            ))
        privacy_manifest = bundle / "PrivacyInfo.xcprivacy"
        if not privacy_manifest.is_file():
            message = f"Falta PrivacyInfo.xcprivacy en {bundle}"
            if require_privacy_manifest:
                raise ValueError(message)
            print(f"ADVERTENCIA: {message}", file=sys.stderr)

    if seen != set(expected_slices):
        raise ValueError("Falta una variante de plataforma del XCFramework")
    if len(set(public_interfaces)) != 1:
        raise ValueError("La API pública Swift difiere entre dispositivo y simulador")
    links = subprocess.run(
        ["otool", "-L", str(FRAMEWORK / "ios-arm64" / "BDIdentityVerification.framework" / "BDIdentityVerification")],
        check=True, text=True, capture_output=True,
    ).stdout
    if "@rpath/CaptureCore.framework/CaptureCore" not in links or "@rpath/CaptureUX.framework/CaptureUX" not in links:
        raise ValueError("Faltan las dependencias dinámicas CaptureCore o CaptureUX")
    verify_existing_checksums()


def make_zip(version: str) -> Path:
    output = ROOT / "dist" / f"BDIdentityVerification-{version}.xcframework.zip"
    output.parent.mkdir(exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(FRAMEWORK.rglob("*")):
                if path.is_symlink():
                    raise ValueError(f"El enlace simbólico requiere una política de empaquetado: {path}")
                if not path.is_file():
                    continue
                relative = path.relative_to(ROOT).as_posix()
                entry = zipfile.ZipInfo(relative, date_time=ZIP_DATE)
                entry.create_system = 3
                entry.compress_type = zipfile.ZIP_DEFLATED
                mode = stat.S_IMODE(path.stat().st_mode)
                entry.external_attr = (stat.S_IFREG | mode) << 16
                with path.open("rb") as source, archive.open(entry, "w", force_zip64=True) as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def replace_once(text: str, pattern: str, replacement: str) -> str:
    result, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"Se esperaba una declaración única en Package.swift para {pattern}")
    return result


def verify_or_update_manifest(version: str, checksum: str, check_only: bool) -> None:
    current = MANIFEST.read_text(encoding="utf-8")
    updated = replace_once(
        current,
        r'^let artifactVersion = "[^"]+"$',
        f'let artifactVersion = "{version}"',
    )
    updated = replace_once(
        updated,
        r'^let artifactChecksum = "[^"]+"$',
        f'let artifactChecksum = "{checksum}"',
    )
    if check_only:
        if current != updated:
            raise ValueError("Package.swift no coincide con el ZIP; regenere el manifiesto")
    else:
        MANIFEST.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Etiqueta SemVer, por ejemplo 1.2.3 o 1.2.4-rc.1")
    parser.add_argument("--check", action="store_true", help="Verificar Package.swift sin modificarlo")
    parser.add_argument("--require-privacy-manifest", action="store_true", help="Exigir el manifiesto de privacidad")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-(?:rc|beta)\.[0-9]+)?", args.version):
        parser.error("--version debe ser una versión SemVer o RC")

    inspect_framework(args.version, args.require_privacy_manifest)
    zip_path = make_zip(args.version)
    checksum = subprocess.run(
        ["swift", "package", "compute-checksum", str(zip_path)],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if checksum != sha256(zip_path):
        raise ValueError("El checksum SwiftPM difiere del SHA-256 del ZIP")
    verify_or_update_manifest(args.version, checksum, args.check)

    print(f"Artefacto: {zip_path}")
    print(f"Checksum SwiftPM: {checksum}")
    print(f"URL de release: {RELEASE_BASE}/{args.version}/{zip_path.name}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f"Preparación SPM detenida: {error}", file=sys.stderr)
        sys.exit(1)
