#!/usr/bin/env python3
"""Compose a platform-specific SPDX predicate for the BuildKit SBOM protocol.

The composer deliberately knows nothing about OCI indexes or in-toto
statements. The generator adds the protocol statement around this predicate;
BuildKit supplies the attestation manifest and binds it to the platform image.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from spdx_tools.common.spdx_licensing import spdx_licensing


GENERATOR_NAME = "cnpg-sbom-generator"
GENERATOR_REPOSITORY = "https://github.com/cloudnative-pg/postgres-extensions-containers"
LICENSE_REF = re.compile(r"LicenseRef-[A-Za-z0-9][A-Za-z0-9.-]*")
LICENSE_OPERATOR = re.compile(r"\s+(?:AND|OR|WITH)\s+")


def path_score(candidate: str, final_name: str) -> tuple[int, int]:
    """Prefer an exact path, then the longest shared path suffix."""

    candidate_parts = tuple(part for part in candidate.lstrip("/").split("/") if part)
    final_parts = tuple(part for part in final_name.lstrip("/").split("/") if part)
    common_suffix = 0
    for candidate_part, final_part in zip(reversed(candidate_parts), reversed(final_parts)):
        if candidate_part != final_part:
            break
        common_suffix += 1
    return common_suffix, int(candidate_parts == final_parts)


def file_id(name: str, value: str) -> str:
    identity = f"{name}\0sha256:{value}".encode()
    return f"SPDXRef-File-final-{hashlib.sha256(identity).hexdigest()[:24]}"


def scancode_licenses(
    document: dict[str, Any],
) -> tuple[dict[str, set[str]], dict[str, dict[str, str]], dict[str, list[str]]]:
    """Return valid ScanCode expressions, definitions, and invalid-match evidence."""

    licenses_by_file: defaultdict[str, set[str]] = defaultdict(set)
    comments_by_file: defaultdict[str, list[str]] = defaultdict(list)

    def parse_expression(expression: str) -> tuple[str | None, str | None]:
        try:
            return str(spdx_licensing.parse(expression, validate=False, strict=True)), None
        except Exception as error:
            return None, str(error)

    for record in document["files"]:
        path = record["path"].lstrip("/")
        for detection in record.get("license_detections", []):
            expression = detection.get("license_expression_spdx")
            if not expression or expression in {"NONE", "NOASSERTION"}:
                continue

            parsed_expression, parse_error = parse_expression(expression)
            if parsed_expression is not None:
                licenses_by_file[path].add(parsed_expression)
                continue

            # ScanCode sometimes aggregates separate matches into an expression
            # that SPDX cannot represent (for example, an exception without
            # its governing license). Keep every valid match expression, while
            # retaining the invalid raw finding as file-level evidence.
            matched_licenses: set[str] = set()
            invalid_matches: list[str] = []
            for match in detection.get("matches", []):
                match_expression = match.get("license_expression_spdx")
                if not match_expression or match_expression in {"NONE", "NOASSERTION"}:
                    continue
                parsed_match, match_error = parse_expression(match_expression)
                if parsed_match is not None:
                    matched_licenses.add(parsed_match)
                    continue
                rule = match.get("rule_identifier")
                start_line = match.get("start_line")
                end_line = match.get("end_line")
                lines = (
                    f"lines {start_line}-{end_line}"
                    if start_line is not None and end_line is not None
                    else f"line {start_line}"
                    if start_line is not None
                    else "line range unavailable"
                )
                invalid_matches.append(
                    f"{match_expression!r} ({rule or 'ScanCode rule unavailable'}, {lines}; "
                    f"{match_error or 'not a valid SPDX expression'})"
                )

            licenses_by_file[path].update(matched_licenses)
            retained = ", ".join(sorted(matched_licenses)) or "none"
            comment = (
                f"ScanCode reported {expression!r}, which is not a valid SPDX license expression"
                f" ({parse_error}). Valid match expressions retained: {retained}."
            )
            if invalid_matches:
                comment += " Match evidence without a valid SPDX expression: " + "; ".join(
                    sorted(invalid_matches)
                ) + "."
            comments_by_file[path].append(comment)

    custom_licenses = {
        license_id
        for expressions in licenses_by_file.values()
        for expression in expressions
        for license_id in LICENSE_REF.findall(expression)
    }
    references = {
        reference["spdx_license_key"]: {
            "extractedText": reference.get("text") or "NOASSERTION",
            "licenseId": reference["spdx_license_key"],
            "name": reference.get("name") or reference["spdx_license_key"],
        }
        for reference in document.get("license_references", [])
        if reference.get("spdx_license_key") in custom_licenses
    }
    for license_id in custom_licenses:
        references.setdefault(license_id, {
            "extractedText": "NOASSERTION",
            "licenseId": license_id,
            "name": license_id,
        })
    return licenses_by_file, references, comments_by_file


def set_document_namespace(document: dict[str, Any], extension_name: str, platform: str) -> None:
    # SPDX element IDs are scoped by namespace; hash the content to prevent
    # distinct SBOMs from sharing identities when consumers combine them.
    content = {key: value for key, value in document.items() if key != "documentNamespace"}
    digest = hashlib.sha256(
        json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    document["documentNamespace"] = (
        "https://github.com/cloudnative-pg/postgres-extensions-containers/"
        f"sbom-generator/v1/documents/{extension_name}/{platform.replace('/', '-')}-{digest}"
    )


def compose(builder_document: dict[str, Any], *,
            extension_name: str,
            builder_path: Path = Path("builder"),
            scancode_report: dict[str, Any] | None = None,
            final_inventory: dict[str, Any],
            platform: str,
            evidence: dict[str, Any] | None = None,
            ) -> dict[str, Any]:
    """Compose raw Syft SPDX and the generator's canonical final inventory."""

    builder = builder_document
    licenses_by_file, custom_licenses, license_comments_by_file = scancode_licenses(
        scancode_report if scancode_report is not None else {"files": []}
    )
    final = final_inventory["files"]
    builder_records = builder["files"]
    relationships = builder["relationships"]
    packages = builder["packages"]
    packages_without_file_analysis = {
        package["SPDXID"]
        for package in packages
        if package.get("filesAnalyzed") is False
    }

    package_ids = {
        package["SPDXID"]
        for package in packages
        if package.get("primaryPackagePurpose") != "FILE"
    }

    all_package_ids = {package["SPDXID"] for package in packages}
    retained_package_ids: set[str] = set()
    owners_by_source_file: defaultdict[str, set[str]] = defaultdict(set)
    for relationship in relationships:
        if relationship["relationshipType"] != "CONTAINS":
            continue
        package_id = relationship["spdxElementId"]
        source_file_id = relationship["relatedSpdxElement"]
        if package_id in package_ids and package_id not in packages_without_file_analysis:
            owners_by_source_file[source_file_id].add(package_id)

    by_checksum: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    all_file_ids = {record["SPDXID"] for record in builder_records}
    for record in builder_records:
        for checksum in record["checksums"]:
            if checksum["algorithm"].upper() == "SHA256":
                by_checksum[checksum["checksumValue"].lower()].append(record)

    composed_files: list[dict[str, Any]] = []
    source_to_final: defaultdict[str, set[str]] = defaultdict(set)
    def add_final_file(record: dict[str, Any], sha256: str) -> None:
        output_record = {
            "SPDXID": file_id(record["name"], sha256),
            "checksums": record["checksums"],
            "copyrightText": "NOASSERTION",
            "fileName": record["name"],
            "licenseConcluded": "NOASSERTION",
            "licenseInfoInFiles": ["NOASSERTION"],
        }
        composed_files.append(output_record)

    for final_record in final:
        final_name = final_record["name"]
        sha256 = next(
            checksum["checksumValue"] for checksum in final_record["checksums"]
            if checksum["algorithm"] == "SHA256"
        )
        candidates = by_checksum.get(sha256, [])
        if not candidates:
            add_final_file(final_record, sha256)
            continue

        owned_candidates = [
            record for record in candidates if record["SPDXID"] in owners_by_source_file
        ]
        candidates = owned_candidates or candidates
        best_score = max(path_score(record["fileName"], final_name) for record in candidates)
        selected = [
            record for record in candidates
            if path_score(record["fileName"], final_name) == best_score
        ]
        selected.sort(key=lambda record: record["SPDXID"])
        source_names = {record["fileName"].lstrip("/") for record in selected}
        if len(source_names) > 1:
            add_final_file(final_record, sha256)
            continue

        source = selected[0]
        new_id = file_id(final_name, sha256)
        output_record = source.copy()
        # Final payload hashes override builder values; retain extra algorithms.
        checksums_by_algorithm = {
            checksum["algorithm"].upper(): {
                "algorithm": checksum["algorithm"].upper(),
                "checksumValue": checksum["checksumValue"].lower(),
            }
            for checksum in source["checksums"] + final_record["checksums"]
        }
        output_record["checksums"] = [
            checksums_by_algorithm[algorithm]
            for algorithm in sorted(checksums_by_algorithm)
        ]
        output_record["SPDXID"] = new_id
        output_record["fileName"] = final_record["name"]
        composed_files.append(output_record)
        for record in selected:
            source_to_final[record["SPDXID"]].add(new_id)

    for record in composed_files:
        source_path = record["fileName"].lstrip("/")
        licenses = licenses_by_file.get(source_path)
        if licenses:
            record["licenseInfoInFiles"] = sorted(
                set(record.get("licenseInfoInFiles", []))
                .union(licenses)
                - {"NONE", "NOASSERTION"}
            )
        comments = license_comments_by_file.get(source_path)
        if comments:
            existing_comment = record.get("licenseComments")
            comment_parts = ([existing_comment] if existing_comment else []) + sorted(set(comments))
            record["licenseComments"] = "\n".join(comment_parts)

    for source_file_id, package_ids_for_file in owners_by_source_file.items():
        final_ids_for_source = source_to_final.get(source_file_id)
        if not final_ids_for_source:
            continue
        retained_package_ids.update(package_ids_for_file)

    composed_relationships: list[dict[str, Any]] = []
    seen_relationships: set[str] = set()
    for relationship in relationships:
        element_id = relationship["spdxElementId"]
        related_id = relationship["relatedSpdxElement"]
        if (
            relationship["relationshipType"] == "CONTAINS"
            and element_id in packages_without_file_analysis
            and related_id in all_file_ids
        ):
            # SPDX forbids file ownership relationships for packages whose
            # file analysis is explicitly disabled.
            continue
        if (
            (element_id in all_file_ids and element_id not in source_to_final)
            or (related_id in all_file_ids and related_id not in source_to_final)
        ):
            continue
        if (
            (element_id in all_package_ids and element_id not in retained_package_ids)
            or (related_id in all_package_ids and related_id not in retained_package_ids)
        ):
            continue
        if element_id not in source_to_final and related_id not in source_to_final:
            composed_relationships.append(relationship.copy())
            continue

        element_ids = source_to_final.get(element_id, {element_id})
        related_ids = source_to_final.get(related_id, {related_id})
        for new_element_id in element_ids:
            for new_related_id in related_ids:
                replacement = relationship.copy()
                replacement["spdxElementId"] = new_element_id
                replacement["relatedSpdxElement"] = new_related_id
                identity = json.dumps(replacement, sort_keys=True, separators=(",", ":"))
                if identity not in seen_relationships:
                    seen_relationships.add(identity)
                    composed_relationships.append(replacement)

    output = deepcopy(builder)
    output["packages"] = [
        package for package in output["packages"]
        if package["SPDXID"] in retained_package_ids
    ]
    output["files"] = composed_files
    output["relationships"] = composed_relationships
    package_by_id = {package["SPDXID"]: package for package in output["packages"]}
    file_by_id = {record["SPDXID"]: record for record in composed_files}
    # SPDX 2.3 section 7.9: SHA1 of sorted, concatenated per-file SHA1 values.
    # https://github.com/spdx/spdx-spec/blob/v2.3/chapters/package-information.md#7.9
    # Syft's verification codes cover the complete builder package. Recompute
    # them for the shipped subset, including files copied to multiple paths.
    for package in output["packages"]:
        contained_ids = {
            relationship["relatedSpdxElement"]
            for relationship in composed_relationships
            if relationship["relationshipType"] == "CONTAINS"
            and relationship["spdxElementId"] == package["SPDXID"]
            and relationship["relatedSpdxElement"] in file_by_id
        }
        sha1s = sorted(
            checksum["checksumValue"]
            for contained_id in contained_ids
            for checksum in file_by_id[contained_id]["checksums"]
            if checksum["algorithm"] == "SHA1"
        )
        package["packageVerificationCode"] = {
            "packageVerificationCodeValue": hashlib.sha1(
                "".join(sha1s).encode("ascii"), usedforsecurity=False
            ).hexdigest(),
        }
    licenses_by_package: defaultdict[str, set[str]] = defaultdict(set)
    for relationship in composed_relationships:
        package = package_by_id.get(relationship.get("spdxElementId"))
        file = file_by_id.get(relationship.get("relatedSpdxElement"))
        if (
            relationship.get("relationshipType") == "CONTAINS"
            and package is not None
            and file is not None
        ):
            licenses_by_package[package["SPDXID"]].update(
                set(file.get("licenseInfoInFiles", [])) - {"NONE", "NOASSERTION"}
            )
    for package_id, licenses in licenses_by_package.items():
        if licenses:
            package = package_by_id[package_id]
            package["licenseInfoFromFiles"] = sorted(
                set(package.get("licenseInfoFromFiles", []))
                .union(licenses)
                - {"NONE", "NOASSERTION"}
            )
    for package in output["packages"]:
        if package.get("licenseDeclared") not in {None, "NONE", "NOASSERTION"}:
            continue
        file_licenses = set(package.get("licenseInfoFromFiles", [])) - {"NONE", "NOASSERTION"}
        if not file_licenses:
            continue
        package["licenseDeclared"] = " AND ".join(
            f"({term})" if LICENSE_OPERATOR.search(term) else term
            for term in sorted(file_licenses)
        )
    extracted = {
        item["licenseId"]: item
        for item in output.get("hasExtractedLicensingInfos", [])
    }
    for license_id in custom_licenses:
        extracted.setdefault(license_id, custom_licenses[license_id])
    output["hasExtractedLicensingInfos"] = [
        extracted[key] for key in sorted(extracted)
    ]
    described_ids = {
        relationship["relatedSpdxElement"]
        for relationship in composed_relationships
        if relationship.get("spdxElementId") == output["SPDXID"]
        and relationship.get("relationshipType") == "DESCRIBES"
    }
    # SPDX still needs a described element when no package owns the payload.
    described_elements = retained_package_ids or {record["SPDXID"] for record in composed_files}
    for package_id in sorted(described_elements):
        if package_id not in described_ids:
            output["relationships"].append({
                "spdxElementId": output["SPDXID"],
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": package_id,
            })
    output["name"] = f"{extension_name}-sbom"
    creation_info = output.setdefault("creationInfo", {})
    creators = list(creation_info.get("creators", []))
    generator_version = os.getenv("SBOM_GENERATOR_REVISION") or "unknown"
    generator_creator = f"Tool: {GENERATOR_NAME}-{generator_version}"
    if generator_creator not in creators:
        creators.append(generator_creator)
    creation_info["creators"] = creators
    metadata = {
        "generator": GENERATOR_NAME,
        "generatorVersion": generator_version,
        "generatorRepository": GENERATOR_REPOSITORY,
        "platform": platform,
        "evidence": evidence or {},
    }
    output["annotations"] = list(output.get("annotations", [])) + [{
        "annotationDate": creation_info.get("created", "1970-01-01T00:00:00Z"),
        "annotationType": "OTHER",
        "annotator": generator_creator,
        "comment": json.dumps(metadata, sort_keys=True, separators=(",", ":")),
        "spdxElementId": "SPDXRef-DOCUMENT",
    }]
    set_document_namespace(output, extension_name, platform)
    return output
