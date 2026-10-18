#!/usr/bin/env python3
"""Validate SPDX JSON documents with the SPDX project's Python validator."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any

from spdx_tools.spdx.parser.jsonlikedict.json_like_dict_parser import JsonLikeDictParser
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document


def validate_spdx_document(document: dict[str, Any]) -> list[str]:
    """Return full-document SPDX validation findings for a raw SPDX JSON dict."""

    try:
        parsed_document = JsonLikeDictParser().parse(document)
    except Exception as error:
        return [f"SPDX JSON parser rejected the document: {error}"]

    return [
        f"{message.context.spdx_id}: {message.validation_message}"
        if message.context and message.context.spdx_id
        else message.validation_message
        for message in validate_full_spdx_document(parsed_document)
    ]


def validate_spdx_file(path: Path) -> list[str]:
    """Validate either a raw SPDX document or a BuildKit statement wrapper."""

    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)
    if isinstance(document, dict) and document.get("predicateType") == "https://spdx.dev/Document":
        document = document.get("predicate")
    if not isinstance(document, dict):
        return ["input does not contain an SPDX JSON object"]
    return validate_spdx_document(document)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an SPDX 2.3 JSON document or BuildKit SPDX statement"
    )
    parser.add_argument("document", type=Path)
    args = parser.parse_args()

    try:
        findings = validate_spdx_file(args.document)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"SPDX document could not be parsed: {error}", file=sys.stderr)
        return 1

    print(f"spdx-tools: {importlib.metadata.version('spdx-tools')}")
    print(f"Validation findings: {len(findings)}")
    for finding in findings:
        print(f"- {finding}")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
