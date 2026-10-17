"""Verify the upstream version and extended-image revision contract offline."""

import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release", ROOT / ".github/scripts/release.py"
)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseVersionTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((ROOT / ".github/release.json").read_text())
        self.version = (ROOT / "version").read_text().strip()

    def choose(self, base, revision, **kwargs):
        return release.choose(
            self.policy, base, "patch", None, kwargs.pop("occupied", lambda _: []),
            base_revision=revision, input_version=self.version, **kwargs
        )

    def test_source_and_image_versions_agree(self):
        self.assertEqual(self.policy["version"]["scheme"], "upstream-revision")
        self.assertEqual(self.policy["version"]["revision_path"], "revision")
        release.version_key(self.version, "semver")
        dockerfile = (ROOT / "Dockerfile").read_text()
        args = dict(re.findall(r"^ARG ([A-Z_]+)=(.+)$", dockerfile, re.M))
        self.assertEqual(args["COMFYUI_VERSION"], self.version)
        self.assertRegex(args["COMFYUI_COMMIT"], r"^[0-9a-f]{40}$")
        revision = (ROOT / "revision").read_text().strip()
        if revision:
            release.revision_number(revision)

    def test_first_release_has_no_revision_suffix(self):
        version, revision, plan = self.choose(self.version, "r0", initial=True)
        self.assertEqual((version, revision), (self.version, "r0"))
        self.assertEqual(plan["release_tag"], self.version)
        self.assertEqual(plan["images"][0]["tag"], self.version)

    def test_first_release_collision_starts_at_r1(self):
        def occupied(plan):
            return ["release_tag"] if plan["release_tag"] == self.version else []

        version, revision, plan = self.choose(
            self.version, "r0", initial=True, occupied=occupied
        )
        self.assertEqual((version, revision), (self.version, "r1"))
        self.assertEqual(plan["images"][0]["tag"], f"{self.version}-r1")

    def test_classification_never_bumps_upstream_version(self):
        for level in ("patch", "minor", "major"):
            with self.subTest(level=level):
                version, revision, _ = release.choose(
                    self.policy, self.version, level, None, lambda _: [],
                    base_revision="r1", input_version=self.version
                )
                self.assertEqual((version, revision), (self.version, "r2"))

    def test_same_upstream_advances_only_revision(self):
        version, revision, plan = self.choose(self.version, "r2")
        self.assertEqual((version, revision), (self.version, "r3"))
        self.assertEqual(plan["release_tag"], f"{self.version}-r3")
        self.assertEqual(plan["images"][0]["tag"], f"{self.version}-r3")

    def test_new_upstream_resets_revision(self):
        version, revision, plan = self.choose("0.40.0", "r8")
        self.assertEqual((version, revision), (self.version, "r0"))
        self.assertEqual(plan["release_tag"], self.version)

    def test_collisions_advance_revision_without_inventing_upstream_version(self):
        seen = []

        def occupied(plan):
            seen.append(plan["release_tag"])
            return ["release_tag", "extended"] if len(seen) == 1 else []

        version, revision, plan = self.choose(self.version, "r2", occupied=occupied)
        self.assertEqual((version, revision), (self.version, "r4"))
        self.assertEqual(seen, [f"{self.version}-r3", f"{self.version}-r4"])
        self.assertEqual(plan["images"][0]["tag"], f"{self.version}-r4")

    def test_upstream_downgrade_is_rejected(self):
        with self.assertRaises(release.PreparationError):
            self.choose("999.0.0", "r0")

    def test_revision_does_not_make_stable_upstream_a_prerelease(self):
        self.assertFalse(release.publication(self.policy, self.version, "r1")["is_prerelease"])

    def test_unlabeled_pr_does_not_publish(self):
        self.assertIsNone(release.classification({"number": 1, "labels": [], "body": "Prepare only"}))


if __name__ == "__main__":
    unittest.main()
