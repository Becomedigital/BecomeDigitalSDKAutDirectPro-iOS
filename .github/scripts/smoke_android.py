#!/usr/bin/env python3
"""Prepara una aplicación consumidora del POM en un repositorio Maven temporal."""

import importlib.util
import json
import os
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]


def prepare(root=ROOT):
    config = json.loads((root / '.github/distribution.json').read_text())
    spec = importlib.util.spec_from_file_location('maven', root / 'scripts/prepare_maven_release.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Este repositorio es efímero y no se firma ni se envía a un registro externo.
    value = (root / 'VERSION').read_text().strip() if (root / 'VERSION').exists() else '1.2.3'
    module.stage(value, 'Prueba local de integración', 'https://example.invalid/ci-only', False, None)
    repository = root / 'dist/maven-repository'
    target = Path(os.environ['RUNNER_TEMP']) / 'become-android-maven-ci'
    shutil.copytree(root / config['android_demo'], target, ignore=shutil.ignore_patterns(
        'build', '.gradle', '.kotlin', 'local.properties', 'credentials.properties'))
    build = target / 'app/build.gradle'
    text, count = re.subn(r'(?ms)^dependencies \{.*?^\}', '''dependencies {
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.5'
    implementation '%s:%s:%s'
}''' % (module.GROUP, module.ARTIFACT, value), build.read_text())
    if count != 1:
        raise ValueError('Se requiere un único bloque de dependencias de la aplicación.')
    build.write_text(text)
    settings = target / 'settings.gradle'
    text = settings.read_text()
    anchor = 'repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories {'
    if text.count(anchor) != 1:
        raise ValueError('No se encontró la configuración de repositorios esperada.')
    settings.write_text(text.replace(anchor, anchor + ' maven { url = uri(' +
        json.dumps(repository.as_uri()) + '); content { includeGroup(' + json.dumps(module.GROUP) + ') } };'))
    with Path(os.environ['GITHUB_ENV']).open('a') as environment:
        environment.write('ANDROID_CI_PROJECT=' + str(target) + '\n')
    print('La aplicación consumirá únicamente la coordenada Maven y sus dependencias transitivas.')


if __name__ == '__main__':
    prepare()
