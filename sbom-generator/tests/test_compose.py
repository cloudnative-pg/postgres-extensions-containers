#!/usr/bin/env python3
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from spdx_tools.spdx.parser.jsonlikedict.json_like_dict_parser import JsonLikeDictParser
from spdx_tools.spdx.spdx_element_utils import calculate_package_verification_code

sys.path.insert(0, str(Path(__file__).parents[1]))

from compose import compose, set_document_namespace  # noqa: E402
from spdx_validation import validate_spdx_document  # noqa: E402


def checksum(value):
    contents = value.encode()
    return [
        {"algorithm": "SHA1", "checksumValue": hashlib.sha1(contents).hexdigest()},
        {"algorithm": "SHA256", "checksumValue": hashlib.sha256(contents).hexdigest()},
    ]


def package(spdxid, name, version, purl):
    return {
        "SPDXID": spdxid,
        "copyrightText": "NOASSERTION",
        "downloadLocation": "NOASSERTION",
        "externalRefs": [{
            "referenceCategory": "PACKAGE-MANAGER",
            "referenceLocator": purl,
            "referenceType": "purl",
        }],
        "filesAnalyzed": True,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": "NOASSERTION",
        "name": name,
        "supplier": "NOASSERTION",
        "versionInfo": version,
    }


def builder_document():
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "builder",
        "creationInfo": {"created": "2026-01-01T00:00:00Z", "creators": ["Tool: syft"]},
        "packages": [
            package("SPDXRef-Package-base", "base", "1", "pkg:deb/debian/base@1?arch=amd64&distro=debian-12.15"),
            package("SPDXRef-Package-extension", "extension", "2", "pkg:deb/debian/extension@2?arch=amd64&distro=debian-12.15"),
            package("SPDXRef-Package-build-only", "build-only", "3", "pkg:deb/debian/build-only@3?arch=amd64&distro=debian-12.15"),
        ],
        "files": [
            {"SPDXID": "SPDXRef-File-base", "fileName": "usr/lib/base.so", "checksums": checksum("base")},
            {"SPDXID": "SPDXRef-File-extension", "fileName": "usr/lib/postgresql/ext.so", "checksums": checksum("extension")},
            {"SPDXID": "SPDXRef-File-build-only", "fileName": "usr/bin/cc", "checksums": checksum("build-only")},
        ],
        "relationships": [
            {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-base"},
            {"spdxElementId": "SPDXRef-Package-extension", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-extension"},
            {"spdxElementId": "SPDXRef-Package-build-only", "relationshipType": "CONTAINS", "relatedSpdxElement": "SPDXRef-File-build-only"},
            {"spdxElementId": "SPDXRef-Package-base", "relationshipType": "DEPENDENCY_OF", "relatedSpdxElement": "SPDXRef-Package-extension"},
        ],
    }


def inventory(*entries):
    records = []
    for name, contents in entries:
        checksums = checksum(contents)
        records.append({
            "name": name,
            "checksums": checksums,
        })
    return {"files": sorted(records, key=lambda record: record["name"])}


class ComposeTest(unittest.TestCase):
    def test_composes_only_shipped_files_and_owned_packages(self):
        output = compose(
            builder_document(),
            extension_name="plr",
            final_inventory=inventory(
                ("lib/ext.so", "extension"),
                ("generated/artifact", "generated"),
            ),
            platform="linux/amd64",
        )
        self.assertEqual(output["name"], "plr-sbom")
        self.assertEqual(
            {record["name"] for record in output["packages"]},
            {"extension"},
        )
        self.assertEqual(
            [record["fileName"] for record in output["files"]],
            ["generated/artifact", "lib/ext.so"],
        )
        self.assertFalse(any(
            relationship["relationshipType"] == "CONTAINS"
            and relationship["relatedSpdxElement"] == output["files"][0]["SPDXID"]
            for relationship in output["relationships"]
        ))
        self.assertNotIn("build-only", json.dumps(output))
        self.assertFalse("subject" in output)

    def test_verification_code_covers_shipped_copies_instead_of_builder_package(self):
        document = builder_document()
        document["packages"][1]["packageVerificationCode"] = {
            "packageVerificationCodeValue": "0" * 40,
            "packageVerificationCodeExcludedFiles": ["builder-only-file"],
        }
        document["files"].append({
            "SPDXID": "SPDXRef-File-other",
            "fileName": "usr/lib/postgresql/other.so",
            "checksums": checksum("other"),
        })
        document["relationships"].append({
            "spdxElementId": "SPDXRef-Package-extension",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-other",
        })
        output = compose(
            document,
            extension_name="demo",
            final_inventory=inventory(
                ("lib/ext.so", "extension"),
                ("lib/duplicate.so", "extension"),
                ("lib/other.so", "other"),
            ),
            platform="linux/amd64",
        )
        # Use SPDX Tools as an independent oracle for sorting and duplicate hashes.
        parsed = JsonLikeDictParser().parse(output)
        self.assertEqual(len(parsed.files), 3)
        expected = calculate_package_verification_code(parsed.files).value
        self.assertEqual(output["packages"][0]["packageVerificationCode"], {
            "packageVerificationCodeValue": expected,
        })
        self.assertEqual(validate_spdx_document(output), [])

    def test_matched_file_uses_final_inventory_sha1_when_builder_only_has_sha256(self):
        document = builder_document()
        source = next(
            item for item in document["files"]
            if item["SPDXID"] == "SPDXRef-File-extension"
        )
        source["checksums"] = [checksum("extension")[1]]

        output = compose(
            document,
            extension_name="plr",
            final_inventory=inventory(("usr/lib/postgresql/ext.so", "extension")),
            platform="linux/amd64",
        )
        file_record = next(
            item for item in output["files"]
            if item["fileName"] == "usr/lib/postgresql/ext.so"
        )

        self.assertEqual(
            {item["algorithm"] for item in file_record["checksums"]},
            {"SHA1", "SHA256"},
        )
        self.assertEqual(validate_spdx_document(output), [])

    @patch.dict(os.environ, {"SBOM_GENERATOR_REVISION": "abc123" * 6 + "abcd"})
    def test_generator_metadata_identifies_version_and_repository(self):
        revision = os.environ["SBOM_GENERATOR_REVISION"]
        output = compose(
            builder_document(),
            extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")),
            platform="linux/amd64",
        )
        generator_annotation = next(
            annotation for annotation in output["annotations"]
            if annotation["annotator"] == f"Tool: cnpg-sbom-generator-{revision}"
        )
        metadata = json.loads(generator_annotation["comment"])
        self.assertIn(f"Tool: cnpg-sbom-generator-{revision}", output["creationInfo"]["creators"])
        self.assertEqual(metadata["generator"], "cnpg-sbom-generator")
        self.assertEqual(metadata["generatorVersion"], revision)
        self.assertEqual(
            metadata["generatorRepository"],
            "https://github.com/cloudnative-pg/postgres-extensions-containers",
        )

    def test_license_files_are_mapped_by_checksum_and_source_ownership(self):
        document = builder_document()
        document["packages"].append(
            package("SPDXRef-Package-copyright", "libgomp1", "1", "pkg:deb/debian/libgomp1@1?arch=amd64&distro=debian-12.15")
        )
        document["files"].append({
            "SPDXID": "SPDXRef-File-copyright",
            "fileName": "usr/share/doc/libgomp1/copyright",
            "checksums": checksum("copyright"),
        })
        document["relationships"].append({
            "spdxElementId": "SPDXRef-Package-copyright",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-copyright",
        })
        output = compose(
            document,
            extension_name="plr",
            final_inventory=inventory(("licenses/system/libgomp1/copyright", "copyright")),
            platform="linux/amd64",
            scancode_report={"files": [{
                "path": "licenses/system/libgomp1/copyright",
                "license_detections": [{"license_expression_spdx": "GPL-2.0-only"}],
            }]},
        )
        file_record = output["files"][0]
        package_record = next(item for item in output["packages"] if item["name"] == "libgomp1")
        self.assertEqual(file_record["licenseInfoInFiles"], ["GPL-2.0-only"])
        self.assertEqual(package_record["licenseDeclared"], "GPL-2.0-only")

    def test_invalid_scancode_aggregate_keeps_valid_matches_and_exception_evidence(self):
        document = builder_document()
        document["packages"].append(
            package(
                "SPDXRef-Package-libgfortran5",
                "libgfortran5",
                "1",
                "pkg:deb/debian/libgfortran5@1?arch=amd64&distro=debian-12.15",
            )
        )
        document["files"].append({
            "SPDXID": "SPDXRef-File-gfortran-copyright",
            "fileName": "usr/share/doc/libgfortran5/copyright",
            "checksums": checksum("gfortran-license-evidence"),
        })
        document["relationships"].append({
            "spdxElementId": "SPDXRef-Package-libgfortran5",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-gfortran-copyright",
        })
        output = compose(
            document,
            extension_name="plr",
            final_inventory=inventory(
                ("licenses/libgfortran5/copyright", "gfortran-license-evidence"),
            ),
            platform="linux/amd64",
            scancode_report={
                "files": [{
                    "path": "licenses/libgfortran5/copyright",
                    "license_detections": [
                        {
                            "license_expression_spdx": (
                                "MIT AND GFDL-1.2-only AND GCC-exception-3.1"
                            ),
                            "matches": [
                                {
                                    "license_expression_spdx": "MIT",
                                    "rule_identifier": "mit_1083.RULE",
                                    "start_line": 216,
                                    "end_line": 233,
                                },
                                {
                                    "license_expression_spdx": "GFDL-1.2-only",
                                    "rule_identifier": "gfdl-1.2_7.RULE",
                                    "start_line": 236,
                                    "end_line": 238,
                                },
                                {
                                    "license_expression_spdx": "GCC-exception-3.1",
                                    "rule_identifier": "gcc-exception-3.1.LICENSE",
                                    "start_line": 241,
                                    "end_line": 312,
                                },
                            ],
                        },
                        {
                            "license_expression_spdx": (
                                "GPL-3.0-or-later WITH GCC-exception-3.1"
                            ),
                        },
                    ],
                }],
            },
        )

        file_record = output["files"][0]
        self.assertEqual(file_record["licenseInfoInFiles"], [
            "GFDL-1.2-only",
            "GPL-3.0-or-later WITH GCC-exception-3.1",
            "MIT",
        ])
        self.assertIn(
            "MIT AND GFDL-1.2-only AND GCC-exception-3.1",
            file_record["licenseComments"],
        )
        self.assertIn("GCC-exception-3.1", file_record["licenseComments"])
        self.assertIn("lines 241-312", file_record["licenseComments"])
        self.assertIn("gcc-exception-3.1.LICENSE", file_record["licenseComments"])
        package_record = next(
            item for item in output["packages"] if item["name"] == "libgfortran5"
        )
        self.assertIn("licenseDeclared", package_record)
        self.assertEqual(validate_spdx_document(output), [])

    def test_unmatched_files_and_scanned_licenses_are_kept_unclaimed(self):
        output = compose(
            builder_document(),
            extension_name="demo",
            final_inventory=inventory(
                ("licenses/vendor/copyright", "vendor-license"),
                ("licenses/other/copyright", "other-license"),
            ),
            platform="linux/amd64",
            scancode_report={"files": [
                {
                    "path": "licenses/vendor/copyright",
                    "license_detections": [{"license_expression_spdx": "LicenseRef-Vendor"}],
                },
                {
                    "path": "licenses/other/copyright",
                    "license_detections": [{
                        "license_expression_spdx": "Apache-2.0 OR BSD-2-Clause",
                    }],
                },
            ], "license_references": [{
                "spdx_license_key": "LicenseRef-Vendor",
                "name": "Vendor license",
                "text": "vendor license text",
            }]},
        )
        self.assertEqual({item["fileName"] for item in output["files"]}, {
            "licenses/vendor/copyright", "licenses/other/copyright",
        })
        self.assertEqual(
            {item["fileName"]: item["licenseInfoInFiles"] for item in output["files"]},
            {
                "licenses/vendor/copyright": ["LicenseRef-Vendor"],
                "licenses/other/copyright": ["Apache-2.0 OR BSD-2-Clause"],
            },
        )
        self.assertEqual(
            [item["licenseId"] for item in output["hasExtractedLicensingInfos"]],
            ["LicenseRef-Vendor"],
        )
        self.assertEqual({item["name"] for item in output["packages"]}, set())
        file_ids = {item["SPDXID"] for item in output["files"]}
        self.assertFalse(any(
            relationship["relationshipType"] == "CONTAINS"
            and relationship["relatedSpdxElement"] in file_ids
            for relationship in output["relationships"]
        ))
        self.assertEqual(validate_spdx_document(output), [])

    def test_platform_documents_are_deterministic_and_isolated(self):
        first = compose(
            builder_document(), extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/amd64",
            evidence={"builderSha256": "abc"},
        )
        second = compose(
            builder_document(), extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/arm64",
            evidence={"builderSha256": "abc"},
        )
        self.assertNotEqual(first["documentNamespace"], second["documentNamespace"])
        self.assertEqual(first, compose(
            builder_document(), extension_name="plr",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/amd64",
            evidence={"builderSha256": "abc"},
        ))

    def test_namespace_changes_with_content_and_is_stable_when_reapplied(self):
        first = compose(
            builder_document(), extension_name="demo",
            final_inventory=inventory(("lib/ext.so", "extension")), platform="linux/amd64",
        )
        changed = compose(
            builder_document(), extension_name="demo",
            final_inventory=inventory(("lib/ext.so", "different")), platform="linux/amd64",
        )
        self.assertNotEqual(first["documentNamespace"], changed["documentNamespace"])
        original_namespace = first["documentNamespace"]
        set_document_namespace(first, "demo", "linux/amd64")
        self.assertEqual(first["documentNamespace"], original_namespace)
        first["comment"] = "Downstream augmentation"
        set_document_namespace(first, "demo", "linux/amd64")
        self.assertNotEqual(first["documentNamespace"], original_namespace)

    def test_files_from_packages_without_file_analysis_are_not_claimed_as_contained(self):
        document = builder_document()
        package_id = "SPDXRef-Package-extension"
        package = next(item for item in document["packages"] if item["SPDXID"] == package_id)
        package["filesAnalyzed"] = False
        output = compose(
            document,
            extension_name="demo",
            final_inventory=inventory(("usr/lib/postgresql/ext.so", "extension")),
            platform="linux/amd64",
        )

        self.assertNotIn(package_id, {item["SPDXID"] for item in output["packages"]})
        self.assertFalse(any(
            relationship["relationshipType"] == "CONTAINS"
            and relationship["relatedSpdxElement"] == output["files"][0]["SPDXID"]
            for relationship in output["relationships"]
        ))
        self.assertEqual(validate_spdx_document(output), [])

    def test_license_path_does_not_claim_package_without_file_analysis(self):
        document = builder_document()
        rust_id = "SPDXRef-Package-rust"
        document["packages"].append(package(
            rust_id, "rust1.97.1", "1.97.1", "pkg:deb/debian/rust1.97.1@1.97.1?arch=amd64"
        ))
        next(item for item in document["packages"] if item["SPDXID"] == rust_id)["filesAnalyzed"] = False
        output = compose(
            document,
            extension_name="demo",
            final_inventory=inventory(("licenses/rust1.97.1/copyright", "rust-license")),
            platform="linux/amd64",
        )

        self.assertNotIn(rust_id, {item["SPDXID"] for item in output["packages"]})
        self.assertFalse(any(
            relationship["relationshipType"] == "CONTAINS"
            and relationship["spdxElementId"] == rust_id
            for relationship in output["relationships"]
        ))



if __name__ == "__main__":
    unittest.main()
