#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))

from generator import (  # noqa: E402
    final_inventory,
    infer_platform,
    scan_licenses,
)


class GeneratorTest(unittest.TestCase):
    def test_inventory_hashes_regular_and_symlink_files_without_following_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lib").mkdir()
            payload = b"payload"
            (root / "lib" / "ext.so").write_bytes(payload)
            (root / "lib" / "alias.so").symlink_to("ext.so")
            (root / "outside").symlink_to("/tmp", target_is_directory=True)
            output = final_inventory(root)
        records = {record["name"]: record for record in output["files"]}
        hashes = {name: {c["algorithm"]: c["checksumValue"] for c in record["checksums"]}
                  for name, record in records.items()}
        self.assertEqual(hashes["lib/ext.so"]["SHA256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(
            next(item["checksumValue"] for item in records["lib/ext.so"]["checksums"] if item["algorithm"] == "SHA1"),
            hashlib.sha1(payload).hexdigest(),
        )
        self.assertNotEqual(hashes["lib/alias.so"]["SHA256"], hashes["lib/ext.so"]["SHA256"])
        alias_sha1 = next(
            item["checksumValue"]
            for item in records["lib/alias.so"]["checksums"]
            if item["algorithm"] == "SHA1"
        )
        self.assertEqual(alias_sha1, hashlib.sha1(b"ext.so").hexdigest())
        self.assertEqual(hashes["outside"]["SHA256"], hashlib.sha256(b"/tmp").hexdigest())

    def test_platform_comes_from_builder_package_architecture(self):
        document = {"packages": [{"externalRefs": [{
            "referenceType": "purl",
            "referenceLocator": "pkg:deb/debian/base@1?arch=amd64&distro=debian-12.15",
        }]}]}
        self.assertEqual(infer_platform(document), "linux/amd64")

    def test_license_files_are_split_before_scancode_and_paths_are_collapsed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "licenses").mkdir()
            (root / "licenses" / "copyright").write_text("license text")
            temporary = root / "temporary"
            temporary.mkdir()
            commands = []

            def fake_csplit(command, **_kwargs):
                if command[0] == "scancode":
                    return fake_scancode(command, **_kwargs)
                commands.append(command)
                prefix = Path(command[command.index("-f") + 1])
                prefix.with_name("license-00").write_text("license text")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            def fake_scancode(command, **_kwargs):
                output = Path(command[command.index("--json") + 1])
                output.write_text(json.dumps({
                    "files": [{
                        "type": "file",
                        "path": "licenses/copyright/license-00",
                        "license_detections": [{
                            "matches": [{"from_file": "licenses/copyright/license-00"}],
                            "license_expression_spdx": "MIT",
                        }],
                    }],
                }))
                return subprocess.CompletedProcess(command, 0)

            with patch("generator.subprocess.run", side_effect=fake_csplit):
                report = scan_licenses(root, temporary)

        self.assertEqual(report["files"][0]["path"], "licenses/copyright")
        self.assertEqual(
            report["files"][0]["license_detections"][0]["matches"][0]["from_file"],
            "licenses/copyright",
        )
        split_command = next(command for command in commands if command[0] == "csplit")
        self.assertIn("/^License:/", split_command)
        self.assertIn("{*}", split_command)


if __name__ == "__main__":
    unittest.main()
