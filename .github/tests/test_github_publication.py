"""Regresiones de publicación cuando la API por tag aún no ve el borrador."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('github_publication_checks', Path(__file__).resolve().parents[1] / 'scripts/distribution.py')
d = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(d)


class DraftPublication(unittest.TestCase):
    def exercise(self, existing=True, target='approved', duplicates=False, listing_error=False):
        state = {'created': existing, 'published': False, 'mutations': [], 'create_requests': []}
        draft = {'id': 17, 'tag_name': '3.5.1-rc.1', 'draft': True, 'prerelease': True,
                 'target_commitish': target, 'assets': []}

        def optional(endpoint):
            # El tag no existe y el endpoint por tag no devuelve borradores.
            self.assertTrue('/git/ref/tags/' in endpoint or '/releases/tags/' in endpoint)
            return None

        def api(endpoint, *args, data=None):
            if endpoint.endswith('/releases') and data is not None:
                state['created'] = True
                state['create_requests'].append(data)
                return dict(draft)
            if '/releases?per_page=' in endpoint:
                if listing_error:
                    raise d.Invalid('GitHub rechazó la consulta: HTTP 403')
                return [[draft, dict(draft, id=18)]] if duplicates else [[draft] if state['created'] else []]
            if endpoint.endswith('/releases/17'):
                return dict(draft)
            if '/releases/tags/' in endpoint:
                raise d.Invalid('gh: Not Found (HTTP 404)')
            self.fail('Consulta inesperada: ' + endpoint)

        def run(*args, **kwargs):
            if args[:3] == ('git', 'rev-parse', 'HEAD'):
                return 'approved'
            state['mutations'].append(args)
            if args[:3] == ('gh', 'release', 'create'):
                state['created'] = True
            if args[:3] == ('gh', 'release', 'edit'):
                state['published'] = True
            return ''

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            for name in ('NOTAS.md', 'SHA256SUMS', 'artefactos.json'):
                (output / name).write_text('Contenido aprobado')
            with patch.object(d, 'release_record', return_value=({}, '')), patch.object(d, 'optional_gh', side_effect=optional), patch.object(d, 'gh_json', side_effect=api), patch.object(d, 'run', side_effect=run):
                d.publish_github({'repository': 'o/r'}, '3.5.1-rc.1', output)
        return state

    def test_first_publication_uses_created_draft_without_querying_it_by_tag(self):
        state = self.exercise(existing=False)
        self.assertTrue(state['published'])
        self.assertEqual(len(state['create_requests']), 1)
        self.assertEqual(state['create_requests'][0]['target_commitish'], 'approved')
        self.assertTrue(state['create_requests'][0]['draft'])

    def test_retry_reuses_existing_draft_instead_of_creating_a_duplicate(self):
        state = self.exercise()
        self.assertTrue(state['published'])
        self.assertFalse(state['create_requests'])
        self.assertFalse(any(call[:3] == ('gh', 'release', 'create') for call in state['mutations']))
        self.assertEqual(sum(call[:3] == ('gh', 'release', 'upload') for call in state['mutations']), 3)

    def test_draft_for_another_commit_is_rejected(self):
        with self.assertRaisesRegex(d.Invalid, 'borrador.*otro commit'):
            self.exercise(target='unapproved')

    def test_ambiguous_drafts_are_not_overwritten(self):
        with self.assertRaisesRegex(d.Invalid, 'más de una publicación'):
            self.exercise(duplicates=True)

    def test_listing_permission_failure_is_not_interpreted_as_absence(self):
        with self.assertRaisesRegex(d.Invalid, 'HTTP 403'):
            self.exercise(listing_error=True)

    def test_sonatype_validation_errors_identify_the_failure_without_credentials(self):
        status = {'errors': {'identity-verification.pom.asc': ['Could not find a public key', 'token=private-token']},
                  'unrelated_response_field': 'do-not-print-this-field'}
        with patch.dict(os.environ, {'MAVEN_CENTRAL_PASSWORD': 'private-token'}):
            message = d.central_validation_failure(status, 'deployment-123')
        self.assertIn('deployment-123', message)
        self.assertIn('Could not find a public key', message)
        self.assertNotIn('private-token', message)
        self.assertNotIn('do-not-print-this-field', message)


if __name__ == '__main__':
    unittest.main()
