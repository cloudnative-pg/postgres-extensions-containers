#!/usr/bin/env python3
"""BuildKit SBOM generator for the final extension payload.

The scanner consumes only the files BuildKit mounts for this invocation.  The
builder stage is evidence for package ownership; the final stage is inventoried
directly.  The output is one BuildKit SBOM-bundle entry: an in-toto Statement
whose predicate is the composed SPDX document.  BuildKit owns the OCI
attestation and image/index binding around that statement.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Sequence

from compose import compose, set_document_namespace
from hooks import HookContext, run_augmentation_hook
from spdx_validation import validate_spdx_document


PLATFORM_ARCHITECTURES = {
    "amd64": "linux/amd64",
    "x86_64": "linux/amd64",
    "arm64": "linux/arm64",
    "aarch64": "linux/arm64",
}

INTOTO_STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
SPDX_PREDICATE_TYPE = "https://spdx.dev/Document"
PROGRESS_INTERVAL_SECONDS = 10


def require_directory(value: str | None, variable: str) -> Path:
    if not value:
        raise RuntimeError(f"{variable} is required")
    path = Path(value)
    if not path.is_dir():
        raise RuntimeError(f"{variable} does not name a directory: {path}")
    return path


def find_builder(extra_root: Path) -> Path:
    """Find the explicitly requested ``builder`` stage in BuildKit extras."""

    builder = extra_root / "sbom-builder"
    if not builder.is_dir():
        raise RuntimeError(f"missing builder mount: {builder}")
    return builder


def file_checksums(path: Path) -> dict[str, str]:
    """Return the SHA1 and SHA256 checksums required by SPDX 2.3."""

    sha1 = hashlib.sha1(usedforsecurity=False)
    sha256 = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha1.update(chunk)
            sha256.update(chunk)
    return {"sha1": sha1.hexdigest(), "sha256": sha256.hexdigest()}


def final_inventory(root: Path) -> dict[str, Any]:
    """Inventory regular files and symlinks without leaving ``root``."""

    records: list[dict[str, Any]] = []

    def add_symlink(path: Path) -> None:
        relative = path.relative_to(root).as_posix()
        target = os.readlink(path).encode()
        records.append({
            "name": relative,
            "checksums": [
                {"algorithm": "SHA1", "checksumValue": hashlib.sha1(target).hexdigest()},
                {"algorithm": "SHA256", "checksumValue": hashlib.sha256(target).hexdigest()},
            ],
        })

    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        for name in list(directory_names):
            path = Path(directory) / name
            if path.is_symlink():
                # os.walk lists symlinked directories separately. Record the
                # link itself but never recurse through a target outside root.
                add_symlink(path)
                directory_names.remove(name)
        for name in file_names:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                # Hash the link payload, never its target. This keeps links
                # outside the mounted filesystem from being followed.
                add_symlink(path)
                continue
            elif path.is_file():
                checksums = file_checksums(path)
            else:
                raise RuntimeError(f"unsupported final filesystem entry: {path}")
            records.append({
                "name": relative,
                "checksums": [
                    {"algorithm": "SHA1", "checksumValue": checksums["sha1"]},
                    {"algorithm": "SHA256", "checksumValue": checksums["sha256"]},
                ],
            })
    if not records:
        raise RuntimeError(f"final filesystem is empty: {root}")
    return {"files": sorted(records, key=lambda record: record["name"])}


def progress(message: str) -> None:
    print(f"sbom-generator: {message}", file=sys.stderr, flush=True)


def run_command_with_progress(
    command: Sequence[str], label: str
) -> subprocess.CompletedProcess:
    """Run a scanner while keeping long-running phases visible in BuildKit logs."""

    progress(f"{label} started")
    started = time.monotonic()
    process = subprocess.Popen(
        list(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    while True:
        try:
            stdout, stderr = process.communicate(timeout=PROGRESS_INTERVAL_SECONDS)
            break
        except subprocess.TimeoutExpired:
            progress(
                f"{label} still running "
                f"({time.monotonic() - started:.0f}s elapsed)"
            )

    result = subprocess.CompletedProcess(
        list(command), process.returncode, stdout, stderr
    )
    elapsed = time.monotonic() - started
    if result.returncode:
        detail = (result.stderr or result.stdout or "scanner failed").strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    progress(f"{label} complete in {elapsed:.1f}s")
    return result


def scan_builder(builder: Path, temporary: Path) -> dict[str, Any]:
    output = temporary / "builder.spdx.json"
    # Design goal: mirror BuildKit's default generator's builder scan.
    # Inspected docker/buildkit-syft-scanner commit fcec6730cc202a3536676eb417b2f7a32fb98854.
    # https://github.com/docker/buildkit-syft-scanner/blob/fcec6730cc202a3536676eb417b2f7a32fb98854/internal/target.go
    # Match its base path, source alias, image/file defaults, and added SBOM cataloger.
    # Recheck these CLI equivalents against upstream when updating Syft.
    run_command_with_progress(
        ["syft", f"dir:{builder}", "--quiet",
         "--base-path", str(builder), "--source-name", builder.name,
         "--override-default-catalogers", "image,file",
         "--select-catalogers", "+sbom-cataloger",
         "--output", f"spdx-json={output}"],
        "Syft builder scan",
    )
    with output.open(encoding="utf-8") as stream:
        document = json.load(stream)
    progress(f"Syft found {len(document['packages'])} builder packages")
    return document


def infer_platform(builder_document: dict[str, Any]) -> str:
    explicit = os.getenv("SBOM_TARGET_PLATFORM") or os.getenv("BUILDKIT_SCAN_PLATFORM")
    if explicit:
        if explicit not in {"linux/amd64", "linux/arm64"}:
            raise RuntimeError(f"unsupported target platform: {explicit}")
        return explicit

    architectures: set[str] = set()
    for package in builder_document.get("packages", []):
        for reference in package.get("externalRefs", []):
            if reference.get("referenceType") != "purl":
                continue
            locator = reference.get("referenceLocator", "")
            for part in locator.split("?")[-1].split("&"):
                key, _, value = part.partition("=")
                if key == "arch" and value in PLATFORM_ARCHITECTURES:
                    architectures.add(value)
    platforms = {PLATFORM_ARCHITECTURES[architecture] for architecture in architectures}
    if len(platforms) != 1:
        raise RuntimeError(
            "cannot determine target platform from builder package evidence; "
            "set SBOM_TARGET_PLATFORM explicitly"
        )
    return next(iter(platforms))


def statement_for(predicate: dict[str, Any]) -> dict[str, Any]:
    """Wrap one SPDX predicate in the statement format BuildKit unbundles.

    BuildKit v0.32's bundle exporter parses scanner output as an in-toto
    Statement. It replaces the empty subject with the final image subject when
    it attaches the statement, so the generator does not guess an image digest.
    """

    return {
        "_type": INTOTO_STATEMENT_TYPE,
        "predicateType": SPDX_PREDICATE_TYPE,
        "predicate": predicate,
        "subject": [],
    }


def generate() -> Path:
    source = require_directory(os.getenv("BUILDKIT_SCAN_SOURCE"), "BUILDKIT_SCAN_SOURCE")
    extras = require_directory(
        os.getenv("BUILDKIT_SCAN_SOURCE_EXTRAS"), "BUILDKIT_SCAN_SOURCE_EXTRAS"
    )
    destination = require_directory(
        os.getenv("BUILDKIT_SCAN_DESTINATION"), "BUILDKIT_SCAN_DESTINATION"
    )
    builder = find_builder(extras)
    if any(destination.iterdir()):
        raise RuntimeError(f"scanner output directory must be empty: {destination}")

    extension_name = os.getenv("SBOM_EXTENSION_NAME", "extension")
    progress(f"starting SBOM for {extension_name}")
    with tempfile.TemporaryDirectory(prefix="cnpg-sbom-") as temporary_name:
        temporary = Path(temporary_name)
        builder_document = scan_builder(builder, temporary)
        platform = infer_platform(builder_document)
        progress(f"target platform: {platform}")
        inventory = final_inventory(source)
        progress(f"final payload inventory contains {len(inventory['files'])} files")
        progress("composing SPDX document")
        predicate = compose(
            builder_document,
            final_inventory=inventory,
        )
        predicate = run_augmentation_hook(predicate, HookContext(
            extension_name=extension_name,
            platform=platform,
            builder_path=builder,
            final_path=source,
            builder_document=builder_document,
        ))
        # Include any downstream augmentation in the final document identity.
        set_document_namespace(predicate, extension_name, platform)
        findings = validate_spdx_document(predicate)
        if findings:
            formatted_findings = "\n".join(f"  - {finding}" for finding in findings)
            raise RuntimeError(
                f"generated SPDX document failed validation ({len(findings)} finding(s)):\n"
                f"{formatted_findings}"
            )
        statement = statement_for(predicate)
        output = destination / "final-payload.spdx.json"
        progress("writing SPDX attestation")
        with output.open("w", encoding="utf-8") as stream:
            json.dump(statement, stream, indent=2, sort_keys=True)
            stream.write("\n")
    return output


def main() -> int:
    try:
        output = generate()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"sbom-generator: {error}", file=sys.stderr)
        return 1
    print(f"wrote {output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
