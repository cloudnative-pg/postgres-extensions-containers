#!/usr/bin/env python3
"""Publish commit images and promote checked digests from the release workflow."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()


def digest_for(reference, allow_missing=False):
    try:
        digest = run("docker", "buildx", "imagetools", "inspect", reference,
                     "--format", "{{.Manifest.Digest}}")
    except subprocess.CalledProcessError as error:
        # Only an explicit missing manifest permits creating a commit tag.
        # Authentication, rate limit, and transport failures must stop the run.
        if allow_missing and error.stderr.strip() == f"ERROR: {reference}: not found":
            return None
        raise
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"Invalid image digest for {reference}: {digest!r}")
    return digest


def verify_image(image, digest, revision, repository):
    configs = json.loads(run("docker", "buildx", "imagetools", "inspect",
                             f"{image}@{digest}", "--format", "{{json .Image}}"))
    for platform in ("linux/amd64", "linux/arm64"):
        config = configs.get(platform, {})
        if f"{config.get('os')}/{config.get('architecture')}" != platform:
            raise ValueError(f"Missing expected platform: {platform}")
        labels = config.get("config", {}).get("Labels", {})
        if labels.get("org.opencontainers.image.revision") != revision:
            raise ValueError(f"Unexpected source revision for {platform}")
        if labels.get("org.opencontainers.image.source") != f"https://github.com/{repository}":
            raise ValueError(f"Unexpected source repository for {platform}")


def build(image, revision, repository, output):
    output.mkdir(parents=True, exist_ok=True)
    reference = f"{image}:sha-{revision}"
    digest = digest_for(reference, allow_missing=True)
    if digest is None:
        # Stream build progress so long builds remain observable in Actions.
        subprocess.run([
            "docker", "buildx", "build", "--platform", "linux/amd64,linux/arm64",
            "--provenance=mode=max",
            "--sbom=true",
            "--build-arg", f"SBOM_GENERATOR_REVISION={revision}",
            "--label", f"org.opencontainers.image.source=https://github.com/{repository}",
            "--tag", reference, "--metadata-file", str(output / "build.json"),
            "--push", "sbom-generator",
        ], check=True)
        metadata = json.loads((output / "build.json").read_text())
        digest = metadata["containerimage.digest"]
        if digest_for(reference) != digest:
            raise ValueError("Published commit tag differs from build metadata")
    else:
        print(f"Reusing {reference}@{digest}", flush=True)
    verify_image(image, digest, revision, repository)
    (output / "digest").write_text(digest + "\n")
    return digest


def promote(image, digest, revision, alias):
    if digest_for(f"{image}:sha-{revision}") != digest:
        raise ValueError("Commit tag no longer identifies the checked digest")
    subprocess.run([
        "docker", "buildx", "imagetools", "create", "--tag", f"{image}:{alias}",
        f"{image}@{digest}",
    ], check=True)
    if digest_for(f"{image}:{alias}") != digest:
        raise ValueError("Promoted alias differs from checked digest")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("build", "promote"))
    parser.add_argument("--image", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--alias", choices=("latest", "test"))
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        parser.error("revision must be a full Git commit SHA")
    if args.operation == "build":
        build(args.image, args.revision, args.repository, args.output)
    else:
        if args.alias is None:
            parser.error("promote requires --alias")
        digest = (args.output / "digest").read_text().strip()
        promote(args.image, digest, args.revision, args.alias)
        (args.output / "promotion.json").write_text(json.dumps({
            "alias": args.alias, "promoted": True, "digest": digest,
        }) + "\n")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        if error.stderr:
            print(error.stderr, file=sys.stderr, end="")
        raise
