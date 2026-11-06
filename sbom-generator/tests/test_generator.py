#!/usr/bin/env python3
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from generator import (  # noqa: E402
    final_inventory,
    infer_platform,
    scan_builder,
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

    def test_builder_scan_uses_image_inventory_and_embedded_sboms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            builder = root / "builder"
            builder.mkdir()
            (builder / "go.mod").write_text(
                "module example.com/source-only\n\ngo 1.22\n\n"
                "require github.com/google/uuid v1.6.0\n"
            )
            metadata = builder / "usr/lib/python3/dist-packages/installed_example-1.2.3.dist-info/METADATA"
            metadata.parent.mkdir(parents=True)
            metadata.write_text("Metadata-Version: 2.1\nName: installed-example\nVersion: 1.2.3\n")
            (builder / "sbom.cdx.json").write_text(json.dumps({
                "bomFormat": "CycloneDX", "specVersion": "1.5", "version": 1,
                "components": [{"type": "library", "name": "embedded-example", "version": "2.3.4"}],
            }))
            output = scan_builder(builder, root)
        packages = {package["name"]: package for package in output["packages"]}
        self.assertEqual(packages["installed-example"]["versionInfo"], "1.2.3")
        self.assertEqual(packages["embedded-example"]["versionInfo"], "2.3.4")
        self.assertNotIn("github.com/google/uuid", packages)
        self.assertNotIn("example.com/source-only", packages)
        record = next(file for file in output["files"] if file["fileName"].endswith("/METADATA"))
        self.assertEqual({c["algorithm"] for c in record["checksums"]}, {"SHA1", "SHA256"})
        self.assertEqual(output["name"], "builder")

    def test_platform_comes_from_builder_package_architecture(self):
        document = {"packages": [{"externalRefs": [{
            "referenceType": "purl",
            "referenceLocator": "pkg:deb/debian/base@1?arch=amd64&distro=debian-12.15",
        }]}]}
        self.assertEqual(infer_platform(document), "linux/amd64")

if __name__ == "__main__":
    unittest.main()
