"""Exercise automatic merge releases against an isolated local Git remote."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "merge_release", ROOT / ".github/scripts/release.py"
)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class GitHubFixture:
    def __init__(self):
        self.prs = {}
        self.merges = {}

    def repo(self, path=""):
        if not path:
            return {"default_branch": "main"}
        if path.startswith("/pulls/"):
            return self.prs[int(path.rsplit("/", 1)[1])]
        raise AssertionError(path)

    def pages(self, path):
        number = int(path.split("/")[2])
        return [{"event": "merged", "commit_id": self.merges[number]}]

    def commit_associations(self, commits):
        for sha in commits:
            yield sha, [
                {"number": number, "merged": True, "baseRefName": "main"}
                for number, merge in self.merges.items() if merge == sha
            ]

    def commit_prs(self, commits):
        for _, prs in self.commit_associations(commits):
            yield from prs

    def add(self, number, base, merge):
        self.prs[number] = {"number": number, "base": {"sha": base},
                            "labels": [], "body": ""}
        self.merges[number] = merge


class MergeReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="merge-release-test-")
        self.addCleanup(temporary.cleanup)
        parent = Path(temporary.name)
        self.bare, self.work = parent / "origin.git", parent / "work"
        self.bare.mkdir()
        self.work.mkdir()
        self.git(self.bare, "init", "--bare", "--initial-branch=main")
        self.git(self.work, "init", "--initial-branch=main")
        for key, value in {"user.name": "Fixture", "user.email": "fixture@example.invalid",
                           "commit.gpgsign": "false", "tag.gpgsign": "false"}.items():
            self.git(self.work, "config", key, value)
        self.git(self.work, "remote", "add", "origin", str(self.bare))
        (self.work / "README.md").write_text("Fixture\n")
        self.git(self.work, "add", ".")
        self.git(self.work, "commit", "-m", "Initial fixture")
        self.initial = self.git(self.work, "rev-parse", "HEAD")
        for name in ("Dockerfile", "version", "revision", ".github/release.json"):
            target = self.work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        # Adoption starts before numbering, even when these tests run at rN.
        (self.work / "revision").write_text("")
        self.version = (ROOT / "version").read_text().strip()
        self.git(self.work, "add", ".")
        self.git(self.work, "commit", "-m", "Introduce automatic release")
        self.source = self.git(self.work, "rev-parse", "HEAD")
        self.git(self.work, "push", "origin", "main")
        self.repo = release.Git(self.work)
        self.gh = GitHubFixture()
        self.gh.add(1, self.initial, self.source)
        collisions = patch.object(release, "remote_collisions", return_value=[])
        collisions.start()
        self.addCleanup(collisions.stop)

    @staticmethod
    def git(directory, *args):
        return subprocess.check_output(
            ["git", "-C", str(directory), *args], stderr=subprocess.PIPE
        ).decode().strip()

    def prepare(self, run_id, source):
        result = release.prepare(self.repo, self.gh, str(run_id), source)
        self.assertEqual(result["publish"], "true")
        self.assertEqual(self.repo.fetch_main(), result["release_sha"])
        self.assertEqual(self.repo.text("rev-list", "-n", "1", result["release_tag"]),
                         result["release_sha"])
        return result

    def merge(self, number, changes):
        base = self.repo.fetch_main()
        tree = self.repo.patch_tree(base, changes)
        source = self.repo.commit(tree, base, "Fixture squash merge")
        self.repo.command("push", "origin", f"{source}:refs/heads/main")
        self.gh.add(number, base, source)
        return source

    def test_unlabeled_merge_publishes_and_duplicate_runs_reuse_or_skip(self):
        first = self.prepare(101, self.source)
        self.assertEqual(first["release_tag"], self.version)
        self.assertEqual(self.repo.blob(first["release_sha"], "revision"), b"r0\n")
        self.assertEqual(self.prepare(101, self.source), first)
        self.assertEqual(release.prepare(self.repo, self.gh, "102", self.source),
                         {"publish": "false"})
        self.assertEqual(self.repo.fetch_main(), first["release_sha"])
        self.assertEqual(self.repo.text("tag").splitlines(), [self.version])

    def test_same_upstream_image_change_only_advances_revision(self):
        self.prepare(101, self.source)
        source = self.merge(2, {"Dockerfile": (self.work / "Dockerfile").read_bytes()
                               + b"\nLABEL fixture=maintenance\n"})
        second = self.prepare(102, source)
        self.assertEqual(second["release_tag"], self.version + "-r1")
        self.assertEqual(second["version"], self.version)

    def test_new_upstream_restarts_at_r0(self):
        self.prepare(101, self.source)
        next_major = release.version_key(self.version, "semver")[0][0] + 1
        version = f"{next_major}.0.0"
        source = self.merge(2, {"version": (version + "\n").encode(), "revision": b""})
        second = self.prepare(102, source)
        self.assertEqual(second["release_tag"], version)
        self.assertEqual(self.repo.blob(second["release_sha"], "revision"), b"r0\n")

    def test_direct_push_without_a_merged_pr_does_not_publish(self):
        self.gh.prs.clear()
        self.gh.merges.clear()
        self.assertEqual(release.prepare(self.repo, self.gh, "101", self.source),
                         {"publish": "false"})
        self.assertEqual(self.repo.fetch_main(), self.source)

    def test_missing_squash_base_evidence_stops_before_numbering(self):
        self.gh.prs[1]["base"] = {}
        with self.assertRaises(release.PreparationError):
            release.prepare(self.repo, self.gh, "101", self.source)
        self.assertEqual(self.repo.fetch_main(), self.source)

    def test_merge_commit_is_rejected_before_numbering(self):
        merge = self.repo.command(
            "commit-tree", self.repo.text("rev-parse", self.source + "^{tree}"),
            "-p", self.source, "-p", self.initial, data=b"Fixture merge commit\n",
        ).decode().strip()
        self.repo.command("push", "origin", f"{merge}:refs/heads/main")
        self.gh.add(1, self.initial, merge)
        with self.assertRaises(release.PreparationError):
            release.prepare(self.repo, self.gh, "101", merge)
        self.assertEqual(self.repo.fetch_main(), merge)
        self.assertEqual(self.repo.text("tag"), "")


if __name__ == "__main__":
    unittest.main()
