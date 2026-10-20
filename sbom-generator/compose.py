#!/usr/bin/env python3
"""Compose a platform-specific SPDX predicate for the BuildKit SBOM protocol.

The composer deliberately knows nothing about OCI indexes or in-toto
statements. The generator adds the protocol statement around this predicate;
BuildKit supplies the attestation manifest and binds it to the platform image.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from copy import deepcopy
from typing import Any


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
            final_inventory: dict[str, Any],
            ) -> dict[str, Any]:
    """Scope Syft SPDX to the final inventory, preserving its other metadata.

    The generator finalizes the namespace after downstream augmentation.
    """

    builder = builder_document
    final = final_inventory["files"]
    builder_records = builder["files"]
    relationships = builder["relationships"]
    packages = builder["packages"]
    eligible_package_ids = {
        package["SPDXID"]
        for package in packages
        if package.get("primaryPackagePurpose") != "FILE"
        and package.get("filesAnalyzed") is not False
    }

    all_package_ids = {package["SPDXID"] for package in packages}
    retained_package_ids: set[str] = set()
    owners_by_source_file: defaultdict[str, set[str]] = defaultdict(set)
    for relationship in relationships:
        if relationship["relationshipType"] != "CONTAINS":
            continue
        package_id = relationship["spdxElementId"]
        source_file_id = relationship["relatedSpdxElement"]
        if package_id in eligible_package_ids:
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
        output_record["checksums"] = final_record["checksums"] + [
            checksum for checksum in source["checksums"]
            if checksum["algorithm"] not in {"SHA1", "SHA256"}
        ]
        output_record["SPDXID"] = new_id
        output_record["fileName"] = final_record["name"]
        composed_files.append(output_record)
        for record in selected:
            source_to_final[record["SPDXID"]].add(new_id)

    for source_file_id, package_ids_for_file in owners_by_source_file.items():
        final_ids_for_source = source_to_final.get(source_file_id)
        if not final_ids_for_source:
            continue
        retained_package_ids.update(package_ids_for_file)

    removed_ids = (all_file_ids - source_to_final.keys()) | (all_package_ids - retained_package_ids)
    composed_relationships: list[dict[str, Any]] = []
    seen_relationships: set[str] = set()
    for relationship in relationships:
        element_id = relationship["spdxElementId"]
        related_id = relationship["relatedSpdxElement"]
        if element_id in removed_ids or related_id in removed_ids:
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
    return output
