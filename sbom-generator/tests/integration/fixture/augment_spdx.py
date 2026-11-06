"""Add one generic Cargo package to exercise downstream hook augmentation."""


def augment_spdx(document, context):
    assert context.api_version == 1
    document["packages"].append({
        "SPDXID": "SPDXRef-Package-sbom-smoke-crate",
        "name": "sbom-smoke-crate",
        "versionInfo": "1.2.3",
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": "MIT",
        "copyrightText": "NOASSERTION",
        "externalRefs": [{
            "referenceCategory": "PACKAGE-MANAGER",
            "referenceType": "purl",
            "referenceLocator": "pkg:cargo/sbom-smoke-crate@1.2.3",
        }],
    })
    document["relationships"].append({
        "spdxElementId": document["SPDXID"],
        "relationshipType": "DESCRIBES",
        "relatedSpdxElement": "SPDXRef-Package-sbom-smoke-crate",
    })
    return document
