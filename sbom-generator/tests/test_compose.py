#!/usr/bin/env python3
import hashlib
import json
import sys
import unittest
from pathlib import Path

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
        "documentNamespace": "https://example.com/syft/builder",
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
            final_inventory=inventory(
                ("lib/ext.so", "extension"),
                ("generated/artifact", "generated"),
            ),
        )
        self.assertEqual(output["name"], "builder")
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
            final_inventory=inventory(
                ("lib/ext.so", "extension"),
                ("lib/duplicate.so", "extension"),
                ("lib/other.so", "other"),
            ),
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
            final_inventory=inventory(("usr/lib/postgresql/ext.so", "extension")),
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

    def test_preserves_syft_document_metadata_and_unused_license_definitions(self):
        document = builder_document()
        document["comment"] = "Original Syft evidence"
        document["hasExtractedLicensingInfos"] = [
            {"licenseId": "LicenseRef-Z", "name": "Z", "extractedText": "Z text"},
            {"licenseId": "LicenseRef-A", "name": "A", "extractedText": "A text"},
        ]
        output = compose(
            document,
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        for field in ("name", "documentNamespace", "creationInfo", "comment", "hasExtractedLicensingInfos"):
            self.assertEqual(output[field], document[field])
        self.assertNotIn("annotations", output)
        self.assertEqual(validate_spdx_document(output), [])

    def test_preserves_package_metadata_without_promoting_file_licenses(self):
        document = builder_document()
        package = document["packages"][1]
        package["licenseDeclared"] = "NOASSERTION"
        package["licenseConcluded"] = "BSD-3-Clause"
        package["licenseInfoFromFiles"] = ["MIT"]
        package["sourceInfo"] = "Original builder package evidence"
        document["files"][1]["licenseInfoInFiles"] = ["Apache-2.0"]
        extra_checksum = {"algorithm": "MD5", "checksumValue": hashlib.md5(b"extension").hexdigest()}
        document["files"][1]["checksums"].append(extra_checksum)
        document["files"][1]["checksums"][0]["checksumValue"] = "0" * 40
        output = compose(
            document,
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        retained = output["packages"][0].copy()
        retained.pop("packageVerificationCode")
        self.assertEqual(retained, package)
        self.assertEqual(output["files"][0]["licenseInfoInFiles"], ["Apache-2.0"])
        self.assertEqual(output["files"][0]["checksums"], checksum("extension") + [extra_checksum])
        self.assertEqual(validate_spdx_document(output), [])

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
        document["files"][-1]["licenseInfoInFiles"] = ["GPL-2.0-only"]
        document["packages"][-1]["licenseDeclared"] = "GPL-2.0-or-later"
        document["relationships"].append({
            "spdxElementId": "SPDXRef-Package-copyright",
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": "SPDXRef-File-copyright",
        })
        output = compose(
            document,
            final_inventory=inventory(("licenses/system/libgomp1/copyright", "copyright")),
        )
        file_record = output["files"][0]
        package_record = next(item for item in output["packages"] if item["name"] == "libgomp1")
        self.assertEqual(file_record["licenseInfoInFiles"], ["GPL-2.0-only"])
        self.assertEqual(package_record["licenseDeclared"], "GPL-2.0-or-later")
        self.assertNotIn("licenseInfoFromFiles", package_record)

    def test_syft_custom_license_text_and_declarations_are_preserved(self):
        document = builder_document()
        document["packages"][1]["licenseDeclared"] = "LicenseRef-Vendor OR MIT"
        document["files"][1]["licenseInfoInFiles"] = ["LicenseRef-Vendor"]
        document["files"][1]["licenseComments"] = "Evidence supplied by Syft"
        reference = {
            "licenseId": "LicenseRef-Vendor",
            "name": "Vendor license",
            "extractedText": "vendor license text",
        }
        document["hasExtractedLicensingInfos"] = [reference]
        output = compose(
            document,
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        self.assertEqual(output["packages"][0]["licenseDeclared"], "LicenseRef-Vendor OR MIT")
        self.assertEqual(output["files"][0]["licenseInfoInFiles"], ["LicenseRef-Vendor"])
        self.assertEqual(output["files"][0]["licenseComments"], "Evidence supplied by Syft")
        self.assertEqual(output["hasExtractedLicensingInfos"], [reference])
        self.assertEqual(validate_spdx_document(output), [])

    def test_unmatched_notices_remain_inventoried_without_license_assertions(self):
        output = compose(
            builder_document(),
            final_inventory=inventory(("licenses/vendor/copyright", "vendor-license")),
        )
        self.assertEqual(output["packages"], [])
        self.assertEqual(output["files"][0]["fileName"], "licenses/vendor/copyright")
        self.assertEqual(output["files"][0]["licenseInfoInFiles"], ["NOASSERTION"])
        self.assertEqual(output["files"][0]["licenseConcluded"], "NOASSERTION")
        self.assertEqual(validate_spdx_document(output), [])

    def test_platform_documents_are_deterministic_and_isolated(self):
        first = compose(
            builder_document(),
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        second = compose(
            builder_document(),
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        set_document_namespace(first, "plr", "linux/amd64")
        set_document_namespace(second, "plr", "linux/arm64")
        self.assertNotEqual(first["documentNamespace"], second["documentNamespace"])
        repeated = compose(
            builder_document(),
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        set_document_namespace(repeated, "plr", "linux/amd64")
        self.assertEqual(first, repeated)

    def test_namespace_changes_with_content_and_is_stable_when_reapplied(self):
        first = compose(
            builder_document(),
            final_inventory=inventory(("lib/ext.so", "extension")),
        )
        changed = compose(
            builder_document(),
            final_inventory=inventory(("lib/ext.so", "different")),
        )
        set_document_namespace(first, "demo", "linux/amd64")
        set_document_namespace(changed, "demo", "linux/amd64")
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
            final_inventory=inventory(("usr/lib/postgresql/ext.so", "extension")),
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
            final_inventory=inventory(("licenses/rust1.97.1/copyright", "rust-license")),
        )

        self.assertNotIn(rust_id, {item["SPDXID"] for item in output["packages"]})
        self.assertFalse(any(
            relationship["relationshipType"] == "CONTAINS"
            and relationship["spdxElementId"] == rust_id
            for relationship in output["relationships"]
        ))



if __name__ == "__main__":
    unittest.main()
