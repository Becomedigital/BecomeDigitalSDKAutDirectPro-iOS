import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/release_candidate.py"
SPECIFICATION = importlib.util.spec_from_file_location("release_candidate", SCRIPT)
candidate = importlib.util.module_from_spec(SPECIFICATION)
SPECIFICATION.loader.exec_module(candidate)


class ReleaseCandidateTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.run_git("init", "-q", "-b", "main")
        self.run_git("config", "user.email", "fixture@example.test")
        self.run_git("config", "user.name", "Fixture")
        self.write(candidate.CONFIG, json.dumps({
            "platform": "ios", "artifacts": ["BDIdentityVerification.xcframework"]
        }))
        self.write("scripts/prepare_spm_release.py", "# trusted tool\n")
        self.write("Package.swift", 'let artifactVersion = "1.0.0"\nlet artifactChecksum = "previous"\n')
        self.write("VERSION", "1.0.0\n")
        self.main = self.commit()
        self.run_git("switch", "-qc", "release/1.0.1-rc.1")

    def run_git(self, *args):
        return candidate.git(self.root, *args)

    def write(self, name, content):
        file = self.root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)

    def commit(self):
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "Fixture")
        return self.run_git("rev-parse", "HEAD")

    def write_candidate(self):
        self.write("VERSION", "1.0.1\n")
        self.write("BDIdentityVerification.xcframework/Info.plist", "candidate artifact")
        self.write(".github/release.json", '{"version":"1.0.1-rc.1"}')
        self.write("Package.swift", 'let artifactVersion = "1.0.1-rc.1"\nlet artifactChecksum = "new"\n')

    def test_unmerged_candidate_survives_unrelated_main_commit(self):
        self.write_candidate()
        tip = self.commit()
        self.run_git("switch", "-q", "main")
        self.write(".github/scripts/release_candidate.py", "# now available on main\n")
        trust = self.commit()
        candidate.validate_candidate(self.root, trust, tip)
        self.run_git("remote", "add", "origin", str(self.root))
        self.assertEqual(candidate.select(self.root, "1.0.1-rc.1", "release/1.0.1-rc.1",
                                          "refs/heads/main"), tip)
        self.assertEqual(self.run_git("rev-parse", "HEAD"), trust)

    def test_stable_versions_and_untrusted_launch_refs_reject_candidate_branch(self):
        with self.assertRaises(candidate.InvalidCandidate):
            candidate.require_main_rc("1.0.1", "refs/heads/main")
        with self.assertRaises(candidate.InvalidCandidate):
            candidate.require_main_rc("1.0.1-rc.1", "refs/heads/release/1.0.1-rc.1")
        self.assertEqual(candidate.select(self.root, "1.0.0", "", "refs/tags/1.0.0"), self.main)

    def test_candidate_cannot_replace_release_tooling(self):
        self.write_candidate()
        self.write("scripts/prepare_spm_release.py", "# modified\n")
        with self.assertRaisesRegex(candidate.InvalidCandidate, "outside the release files"):
            candidate.validate_candidate(self.root, self.main, self.commit())

    def test_candidate_cannot_change_packaging_configuration(self):
        self.write_candidate()
        self.write(candidate.CONFIG, '{"platform":"ios","artifacts":["different.xcframework"]}')
        with self.assertRaisesRegex(candidate.InvalidCandidate, "distribution settings"):
            candidate.validate_candidate(self.root, self.main, self.commit())

    def test_candidate_cannot_change_swift_package_code(self):
        self.write_candidate()
        self.write("Package.swift", 'let artifactVersion = "1.0.1-rc.1"\nlet extra = "unexpected"\n')
        with self.assertRaisesRegex(candidate.InvalidCandidate, "Only the artifact version"):
            candidate.validate_candidate(self.root, self.main, self.commit())

    def test_candidate_cannot_add_symbolic_link_in_binary_bundle(self):
        self.write_candidate()
        os.symlink("/etc/passwd", self.root / "BDIdentityVerification.xcframework" / "unexpected")
        with self.assertRaisesRegex(candidate.InvalidCandidate, "regular files"):
            candidate.validate_candidate(self.root, self.main, self.commit())
