"""Select an unmerged RC from the trusted publication workflow on main."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ".github/distribution.json"
RC_VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)-rc\.[1-9][0-9]*")
COMMIT_SHA = re.compile(r"[a-f0-9]{40}")
RELEASE_METADATA = {
    CONFIG, ".github/notes.json", ".github/release.json", "CHANGELOG.md",
    "CHECKSUMS.sha256", "Package.swift", "VERSION",
}


class InvalidCandidate(ValueError):
    """The candidate does not satisfy the branch publication rules."""


def require(valid, message):
    if not valid:
        raise InvalidCandidate(message)


def git(root, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=root, text=True).rstrip("\n")


def require_main_rc(version, ref):
    require(ref == "refs/heads/main", "Candidate branches must be selected by the workflow on main.")
    require(RC_VERSION.fullmatch(version), "A candidate branch requires an exact release candidate version.")


def validate_candidate(root, trusted_commit, candidate_commit):
    require(COMMIT_SHA.fullmatch(candidate_commit), "Expected a full candidate commit SHA.")
    base = git(root, "merge-base", trusted_commit, candidate_commit)
    require(base in git(root, "rev-list", "--first-parent", trusted_commit).splitlines(),
            "The candidate must be based on main.")

    trusted_config = json.loads(git(root, "show", f"{trusted_commit}:{CONFIG}"))
    candidate_config = json.loads(git(root, "show", f"{candidate_commit}:{CONFIG}"))
    artifacts = tuple(trusted_config["artifacts"])
    for config in (trusted_config, candidate_config):
        config.pop("source", None)
    require(trusted_config == candidate_config, "The candidate changes distribution settings other than source provenance.")

    changed = git(root, "diff", "--no-renames", "--name-only", "-z", base, candidate_commit).split("\0")
    for path in filter(None, changed):
        allowed = (path in RELEASE_METADATA or
                   any(path == artifact or path.startswith(artifact + "/") for artifact in artifacts) or
                   re.fullmatch(r"legal/LICENSE-[^/]+\.txt", path))
        require(allowed, f"The candidate contains a change outside the release files: {path}")
    release_paths = set(filter(None, changed))
    if release_paths:
        entries = (entry.partition("\t") for entry in git(root, "ls-tree", "-r", "-z", candidate_commit).split("\0"))
        require(all(metadata.startswith(("100644 ", "100755 "))
                    for metadata, _, path in entries if path in release_paths),
                "Candidate release files must be regular files.")

    # Only the trusted workflow loads this new helper. An RC already prepared on
    # an earlier main can lack it and still use the same package and validation code.
    tooling = git(root, "diff", "--name-only", trusted_commit, candidate_commit,
                  "--", "scripts", ".github/scripts", ":(exclude).github/scripts/release_candidate.py")
    require(not tooling, "The candidate must use the release tooling currently on main.")
    if trusted_config["platform"] == "ios":
        def manifest(ref):
            text = git(root, "show", f"{ref}:Package.swift")
            return re.sub(r'^(let artifact(?:Version|Checksum) = )"[^"\r\n]*"$', r'\1""', text, flags=re.MULTILINE)
        require(manifest(trusted_commit) == manifest(candidate_commit),
                "Only the artifact version and checksum may change in Package.swift.")


def select(root, version, branch, ref):
    trusted_commit = git(root, "rev-parse", "HEAD")
    if not branch:
        return trusted_commit
    require_main_rc(version, ref)
    branch_ref = f"refs/heads/{branch}"
    git(root, "check-ref-format", branch_ref)
    git(root, "fetch", "--no-tags", "origin", branch_ref)
    commit = git(root, "rev-parse", "FETCH_HEAD")
    validate_candidate(root, trusted_commit, commit)
    return commit


def preflight(root, version, commit, ref):
    require_main_rc(version, ref)
    trusted_commit = git(root, "rev-parse", "HEAD")
    validate_candidate(root, trusted_commit, commit)
    specification = importlib.util.spec_from_file_location(
        "trusted_distribution", root / ".github/scripts/distribution.py")
    distribution = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(distribution)

    # Check the deployment environment and main ancestry using the trusted checkout.
    publication_config = distribution.load(root / CONFIG)
    distribution.publication_gate(publication_config)
    tags = git(root, "tag", "--list").splitlines()
    require(not any(distribution.VERSION.fullmatch(tag) and
                    distribution.version(tag) > distribution.version(version) for tag in tags),
            "A newer version already exists.")

    # The remaining jobs publish the exact same immutable commit validated by CI.
    git(root, "switch", "--detach", commit)
    distribution.release_record(distribution.load(root / CONFIG), version, root)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["select", "preflight"])
    parser.add_argument("--version", default=os.environ.get("RELEASE_VERSION", ""))
    parser.add_argument("--branch", default=os.environ.get("CANDIDATE_BRANCH", ""))
    parser.add_argument("--commit", default=os.environ.get("CANDIDATE_COMMIT", ""))
    args = parser.parse_args()
    ref = os.environ.get("GITHUB_REF", "")
    if args.operation == "select":
        commit = select(ROOT, args.version, args.branch, ref)
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"commit={commit}\n")
    else:
        preflight(ROOT, args.version, args.commit, ref)


if __name__ == "__main__":
    try:
        main()
    except (InvalidCandidate, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from None
