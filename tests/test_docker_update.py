"""Exercise the public Dockerfile update inputs without network access."""

import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DockerUpdateTests(unittest.TestCase):
    def test_update_inputs_are_single_global_assignments(self):
        dockerfile = (ROOT / "Dockerfile").read_text()
        globals_ = dockerfile.split("\nFROM ", 1)[0]
        args = dict(re.findall(r"^ARG ([A-Z_]+)=(.+)$", globals_, re.M))
        self.assertEqual(args.get("COMFYUI_VERSION"), (ROOT / "version").read_text().strip())
        self.assertRegex(args.get("COMFYUI_COMMIT", ""), r"^[0-9a-f]{40}$")
        self.assertRegex(
            args.get("PYTORCH_IMAGE", ""),
            r"^pytorch/pytorch:[^@]+@sha256:[0-9a-f]{64}$",
        )
        for name in ("COMFYUI_VERSION", "COMFYUI_COMMIT", "PYTORCH_IMAGE"):
            self.assertEqual(dockerfile.count(f"ARG {name}="), 1)
        self.assertEqual(re.findall(r"^FROM (.+)$", dockerfile, re.M), ["${PYTORCH_IMAGE}"])

    def test_source_checkout_accepts_matched_updates_and_rejects_a_stale_pin(self):
        dockerfile = (ROOT / "Dockerfile").read_text()
        checkout = re.search(
            r"(?ms)^RUN (git init /opt/ComfyUI.*?)(?=\n\n|\Z)", dockerfile
        )
        self.assertIsNotNone(checkout)

        def git(directory, *args):
            return subprocess.check_output(
                ["git", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false",
                 "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-C", str(directory), *args],
                stderr=subprocess.PIPE,
            ).decode().strip()

        with tempfile.TemporaryDirectory(prefix="docker-update-test-") as directory:
            root = Path(directory)
            upstream = root / "upstream"
            upstream.mkdir()
            git(upstream, "init", "--initial-branch=main")
            commits = {}
            for version in ("1.2.3", "1.2.4"):
                (upstream / "fixture.txt").write_text(version + "\n")
                git(upstream, "add", "fixture.txt")
                git(upstream, "commit", "-m", "Fixture tag " + version)
                git(upstream, "tag", "v" + version)
                commits[version] = git(upstream, "rev-parse", "HEAD")

            cases = [
                ("1.2.3", commits["1.2.3"], True),
                ("1.2.4", commits["1.2.4"], True),
                ("1.2.4", commits["1.2.3"], False),
            ]
            for index, (version, commit, valid) in enumerate(cases):
                with self.subTest(version=version, matched=valid):
                    target = root / ("checkout-" + str(index))
                    script = checkout.group(1).replace(
                        "/opt/ComfyUI", shlex.quote(str(target))
                    ).replace(
                        "https://github.com/Comfy-Org/ComfyUI.git",
                        shlex.quote(upstream.as_uri()),
                    )
                    result = subprocess.run(
                        ["sh", "-eu", "-c", script],
                        env={**os.environ, "COMFYUI_VERSION": version,
                             "COMFYUI_COMMIT": commit},
                        capture_output=True, text=True,
                    )
                    if valid:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(git(target, "rev-parse", "HEAD"), commit)
                    else:
                        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
