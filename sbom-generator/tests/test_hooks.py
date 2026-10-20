import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))

import generator
from hooks import HookContext, run_augmentation_hook
from compose import set_document_namespace
from test_compose import builder_document


def write_hook(builder, source):
    path = builder / "usr/local/share/cnpg-sbom/augment_spdx.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)


class HookTest(unittest.TestCase):
    def test_absent_hook_preserves_document(self):
        document = {"packages": []}
        with tempfile.TemporaryDirectory() as directory:
            context = HookContext("demo", "linux/amd64", Path(directory), Path(directory), {})
            self.assertIs(run_augmentation_hook(document, context), document)

    def test_hook_receives_full_builder_evidence_and_output_is_wrapped(self):
        evidence = builder_document()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, extras, destination = root / "source", root / "extras", root / "output"
            source.mkdir()
            builder = extras / "sbom-builder"
            builder.mkdir(parents=True)
            destination.mkdir()
            (source / "artifact").write_text("payload")
            write_hook(builder, '''
from hooks import HookContext

def augment_spdx(document, context: HookContext):
    assert context.api_version == 1
    assert context.platform == "linux/amd64"
    assert context.builder_path.is_dir()
    assert context.final_path.is_dir()
    assert "build-only" not in {p["name"] for p in document["packages"]}
    assert "build-only" in {p["name"] for p in context.builder_document["packages"]}
    assert document["files"][0]["SPDXID"]
    assert document["files"][0]["checksums"]
    return {**document, "comment": "downstream dependency version and license information"}
''')
            with patch.dict(os.environ, {
                "BUILDKIT_SCAN_SOURCE": str(source),
                "BUILDKIT_SCAN_SOURCE_EXTRAS": str(extras),
                "BUILDKIT_SCAN_DESTINATION": str(destination),
                "SBOM_TARGET_PLATFORM": "linux/amd64",
            }), patch.object(generator, "scan_builder", return_value=evidence):
                statement = json.loads(generator.generate().read_text())
            self.assertEqual(statement["predicate"]["comment"],
                             "downstream dependency version and license information")
            self.assertEqual(statement["subject"], [])
            self.assertEqual([f["fileName"] for f in statement["predicate"]["files"]], ["artifact"])
            predicate = statement["predicate"]
            namespace = predicate["documentNamespace"]
            self.assertNotEqual(namespace, evidence["documentNamespace"])
            set_document_namespace(predicate, os.getenv("SBOM_EXTENSION_NAME", "extension"), "linux/amd64")
            self.assertEqual(predicate["documentNamespace"], namespace)
            del predicate["comment"]
            set_document_namespace(predicate, os.getenv("SBOM_EXTENSION_NAME", "extension"), "linux/amd64")
            self.assertNotEqual(predicate["documentNamespace"], namespace)
