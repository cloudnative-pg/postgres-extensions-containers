[![CloudNativePG](./logo/cloudnativepg.png)](https://cloudnative-pg.io/)

# CNPG PostgreSQL Extensions Container Images

This repository provides **maintenance scripts** for building **immutable
container images** containing PostgreSQL extensions supported by
[CloudNativePG](https://cloudnative-pg.io/). These images are designed to
integrate seamlessly with the [`image volume extensions` feature](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/)
in CloudNativePG.

For detailed instructions on building the images, see the [BUILD.md file](BUILD.md).

---

## Requirements

- **CloudNativePG** ≥ 1.27
- **PostgreSQL** ≥ 18 (requires the `extension_control_path` feature)
- **Kubernetes** 1.33+ with [ImageVolume feature enabled](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/)

---

## Supported Extensions

- [pgvector](pgvector) - Open-source vector similarity search for PostgreSQL
- [PostGIS](postgis) - Open-source geospatial database extension for PostgreSQL
- [pgAudit](pgaudit) - provides detailed session and object audit logging

---

## Naming & Tagging Convention

Each extension image tag follows this format:

```
<extension-name>:<ext_version>-<timestamp>-<pg_version>-<distro>
```

**Example:**
Building `pgvector` version `0.8.1` on PostgreSQL `18.0` for the `trixie`
distro, with build timestamp `202509101200`, results in:

```
pgvector:0.8.1-202509101200-18-trixie
```

For convenience, **rolling tags** should also be published:

```
pgvector:0.8.1-18-trixie
pgvector:0.8.1-18-trixie
```

This scheme ensures:

- Alignment with the upstream `postgres-containers` base images
- Explicit PostgreSQL and extension versioning
- Multi-distro support

---

## Roadmap / Open Questions

- Should each extension live in its **own dedicated folder**? (YES!)
- Should each extension follow its **own release cycle**? (YES!)
  - Should we track dependencies? (YES: TODO)
  - Should we test/rebuild the extensions that depend on the new one and so forth?
- Must every release pass **smoke tests** (e.g. via [Kind](https://kind.sigs.k8s.io/))? (YES!)
- Should we define policies for:

  - Licensing (must be open source)?
  - Contribution and ownership
  - Governance aligned with the [CloudNativePG project](https://cloudnative-pg.io/)?
- Can contributors propose and maintain additional extensions? (YES)
  - Shall we have a template for a new extension?
- Should each extension have designated **component owners** responsible for
  maintenance, reviews, and release management? (YES)
