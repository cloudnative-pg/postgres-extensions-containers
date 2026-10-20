#!/usr/bin/env python3
"""Assert useful content in the BuildKit smoke SPDX and consumer reports."""

import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"BuildKit SBOM smoke check failed: {message}")


def purl(package: dict) -> str | None:
    for reference in package.get("externalRefs", []):
        if reference.get("referenceType") == "purl":
            return reference.get("referenceLocator")
    return None


def main() -> None:
    if len(sys.argv) != 4:
        fail("usage: check_buildkit_smoke.py SPDX_JSON GRANT_JSON GRYPE_JSON")
    spdx_path, grant_path, grype_path = map(Path, sys.argv[1:])
    document = json.loads(spdx_path.read_text(encoding="utf-8"))
    report = json.loads(grant_path.read_text(encoding="utf-8"))
    grype = json.loads(grype_path.read_text(encoding="utf-8"))

    packages = document.get("packages", [])
    by_name = {package.get("name"): package for package in packages}
    files = {record.get("fileName"): record for record in document.get("files", [])}
    notices = {
        "base-files": "licenses/copyright",
        "libc6": "licenses/libc6/copyright",
        "zlib1g": "licenses/zlib1g/copyright",
    }
    for name, path in notices.items():
        package = by_name.get(name)
        if not package:
            fail(f"package-owned Debian {name} package is absent")
        notice = files.get(path)
        if not notice:
            fail(f"package-owned /{path} file is absent")
        ownership = any(
            relation.get("spdxElementId") == package["SPDXID"]
            and relation.get("relatedSpdxElement") == notice["SPDXID"]
            and relation.get("relationshipType") == "CONTAINS"
            for relation in document.get("relationships", [])
        )
        if not ownership:
            fail(f"{name} does not own the final {path} file")

    # zlib1g has a machine-readable Debian copyright declaration that Syft
    # recognizes. The freeform base-files/libc6 notices still exercise ownership,
    # but no longer receive file-level license detection from a second scanner.
    if by_name["zlib1g"].get("licenseDeclared") != "Zlib":
        fail("Syft's Debian zlib1g Zlib declaration was not preserved")

    crate = next(
        (package for package in packages if purl(package) == "pkg:cargo/sbom-smoke-crate@1.2.3"),
        None,
    )
    if not crate or crate.get("licenseDeclared") != "MIT":
        fail("hook-provided Cargo package or its MIT declaration is absent")

    reported = report["run"]["targets"][0]["evaluation"]["findings"]["packages"]
    cargo = [package for package in reported if package["name"] == "sbom-smoke-crate"
             and package["version"] == "1.2.3"]
    if not any(license["id"] == "MIT" for package in cargo for license in package["licenses"]):
        fail("Grant did not report the hook-provided Cargo package with MIT")
    zlib = [package for package in reported if package["name"] == "zlib1g"]
    if not any(license["id"] == "Zlib" for package in zlib for license in package["licenses"]):
        fail("Grant did not report Syft's Zlib declaration for Debian zlib1g")
    if grype["distro"]["name"] != "debian":
        fail("Grype did not recover the Debian distribution from the SPDX inventory")

    print("BuildKit SBOM smoke passed: Debian notice ownership, hook crate, Grant licenses, Grype distro")


if __name__ == "__main__":
    main()
