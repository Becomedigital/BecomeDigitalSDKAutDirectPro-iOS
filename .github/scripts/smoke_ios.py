#!/usr/bin/env python3
"""Compila la integración pública sin instalar ni ejecutar la aplicación."""

import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
TEMP = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'become-ios-ci'


def invoke(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    swift = subprocess.run(['swift','--version'], text=True, capture_output=True, check=True).stdout
    match = re.search(r'Swift version (\d+)\.(\d+)',swift)
    if not match or tuple(map(int,match.groups())) < (6,4):
        sys.exit('El artefacto requiere Swift 6.4 o posterior. Configura un runner hospedado y Xcode compatibles.')
    manifest = (ROOT/'Package.swift').read_text()
    version = re.search(r'^let artifactVersion = "([^"]+)"',manifest,re.MULTILINE).group(1)
    invoke('python3','scripts/prepare_spm_release.py','--version',version,'--check')
    project = 'Examples/SwiftUIDemo/BecomeSwiftUIDemo.xcodeproj'
    common = ['-project',project,'-scheme','BecomeSwiftUIDemo','-configuration','Release',
              '-derivedDataPath',str(TEMP/'DerivedData'),'-clonedSourcePackagesDirPath',str(TEMP/'Packages'),
              '-onlyUsePackageVersionsFromResolvedFile','-disableAutomaticPackageResolution','-skipPackageUpdates',
              'CODE_SIGNING_ALLOWED=NO','ONLY_ACTIVE_ARCH=NO']
    for destination, archs in [('generic/platform=iOS','arm64'),('generic/platform=iOS Simulator','arm64 x86_64')]:
        invoke('xcodebuild','build',*common,'-destination',destination,'ARCHS='+archs)


if __name__ == '__main__':
    main()
