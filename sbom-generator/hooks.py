"""Versioned downstream extension API for the composed payload SPDX."""

from dataclasses import dataclass
from pathlib import Path
from runpy import run_path
from typing import Any


@dataclass(frozen=True)
class HookContext:
    """Filesystem paths and unfiltered scan evidence available to a hook.

    Treat builder_document as read-only evidence. Filesystem paths are valid
    only during this invocation. The frozen context does not freeze nested JSON.
    """

    extension_name: str
    platform: str
    builder_path: Path
    final_path: Path
    builder_document: dict[str, Any]
    api_version: int = 1


def run_augmentation_hook(document: dict[str, Any], context: HookContext) -> dict[str, Any]:
    """Run the builder's optional hook file, or return the document unchanged."""

    hook_path = context.builder_path / "usr/local/share/cnpg-sbom/augment_spdx.py"
    if not hook_path.exists():
        return document
    try:
        namespace = run_path(str(hook_path))
        return namespace["augment_spdx"](document, context)
    except Exception as error:
        raise RuntimeError(f"SBOM hook {hook_path} failed: {error}") from error
