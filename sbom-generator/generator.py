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
import platform as host_platform
import re
import shutil
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
    run_command_with_progress(
        ["syft", f"dir:{builder}", "--scope", "all-layers", "--quiet",
         "--output", f"spdx-json={output}"],
        "Syft builder scan",
    )
    with output.open(encoding="utf-8") as stream:
        document = json.load(stream)
    progress(f"Syft found {len(document['packages'])} builder packages")
    return document


def scan_licenses(final_root: Path, temporary: Path) -> dict[str, Any]:
    licenses = final_root / "licenses"
    if not licenses.exists():
        return {"files": []}
    scan_root = prepare_license_scan_root(final_root, temporary)
    output = temporary / "scancode.json"
    try:
        subprocess.run(
            [
                "scancode",
                "--verbose",
                "--license",
                "--license-references",
                "--json",
                str(output),
                str(scan_root),
            ],
            stderr=subprocess.STDOUT,
            check=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError("scancode is required when the final payload has /licenses") from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"ScanCode failed with exit code {error.returncode}; see output above") from error
    try:
        with output.open(encoding="utf-8") as stream:
            report = json.load(stream)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"scancode did not produce valid JSON at {output}") from error
    if not isinstance(report, dict):
        raise RuntimeError("scancode output is not a JSON object")
    normalize_scancode_report_paths(report, scan_root)
    return report


def prepare_license_scan_root(final_root: Path, temporary: Path) -> Path:
    """Split shipped copyright files before ScanCode scans them.

    Debian copyright files can contain thousands of ``License:`` sections.
    ScanCode's per-file timeout applies to the combined file, so scan a
    directory of chunks instead and map the chunk paths back afterward.
    """

    licenses = final_root / "licenses"
    scan_root = temporary / "license-chunks" / "licenses"
    started = time.monotonic()
    license_file_count = 0
    chunk_count = 0
    for license_file in sorted(licenses.rglob("*")):
        if license_file.is_symlink() or not license_file.is_file():
            continue
        license_file_count += 1
        relative = license_file.relative_to(licenses)
        chunk_directory = scan_root / relative
        chunk_directory.mkdir(parents=True, exist_ok=True)
        prefix = chunk_directory / "license-"
        try:
            result = subprocess.run(
                [
                    "csplit",
                    "-s",
                    "-z",
                    "-f",
                    str(prefix),
                    str(license_file),
                    "/^License:/",
                    "{*}",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as error:
            raise RuntimeError("csplit is required to prepare license files") from error
        if result.returncode:
            detail = (result.stderr or result.stdout or "csplit failed").strip()
            raise RuntimeError(f"csplit failed for {license_file}: {detail}")
        chunk_count += sum(
            1 for path in chunk_directory.glob("license-*") if path.is_file()
        )
        if license_file_count % 100 == 0:
            progress(
                f"prepared {license_file_count} license files "
                f"({chunk_count} ScanCode chunks, "
                f"{time.monotonic() - started:.1f}s elapsed)"
            )
    progress(
        f"prepared {license_file_count} license files into {chunk_count} "
        f"ScanCode chunks in {time.monotonic() - started:.1f}s"
    )
    return scan_root


def normalize_scancode_report_paths(
    report: dict[str, Any], scan_root: Path
) -> None:
    """Collapse split-file paths to the original final-image paths."""

    scan_prefix = str(scan_root).rstrip("/")
    chunk_suffix = re.compile(r"/license-[0-9]+$")

    def normalize(path: str) -> str:
        if path == scan_prefix:
            path = scan_root.name
        elif path.startswith(f"{scan_prefix}/"):
            path = f"{scan_root.name}/{path[len(scan_prefix) + 1:]}"
        return chunk_suffix.sub("", path.lstrip("/"))

    for record in report["files"]:
        path = record.get("path")
        if isinstance(path, str):
            record["path"] = normalize(path)
        for detection in record.get("license_detections", []):
            for match in detection.get("matches", []):
                from_file = match.get("from_file")
                if isinstance(from_file, str):
                    match["from_file"] = normalize(from_file)


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


def tool_version(command: str) -> str:
    executable = shutil.which(command)
    if not executable:
        return "unavailable"
    try:
        result = subprocess.run(
            [executable, "--version"], check=False, capture_output=True, text=True
        )
    except OSError:
        return "unavailable"
    return (result.stdout or result.stderr).splitlines()[0] if (result.stdout or result.stderr) else "unknown"


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
        report = scan_licenses(source, temporary)
        progress("composing SPDX document")
        evidence = {
            "platformEvidence": "builder package purl architecture",
            "hostArchitecture": host_platform.machine(),
            "tools": {
                "syft": tool_version("syft"),
                "scancode": tool_version("scancode"),
                "python": sys.version.split()[0],
            },
        }
        predicate = compose(
            builder_document,
            extension_name=extension_name,
            builder_path=builder,
            final_inventory=inventory,
            platform=platform,
            scancode_report=report,
            evidence=evidence,
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
