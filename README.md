[![CloudNativePG](./logo/cloudnativepg.png)](https://cloudnative-pg.io/)

# CNPG PostgreSQL Extensions Container Images

This repository provides **maintenance scripts** for building **immutable
container images** containing PostgreSQL extensions supported by
[CloudNativePG](https://cloudnative-pg.io/). These images are designed to
integrate seamlessly with the [`image volume extensions` feature](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/)
in CloudNativePG.

---

## Requirements

- **CloudNativePG** ≥ 1.27
- **PostgreSQL** ≥ 18 (requires the `extension_control_path` feature)
- **Kubernetes** 1.33+ with [ImageVolume feature enabled](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/)

---

## Supported Extensions

- **pgaudit** - PostgreSQL Audit Extension for detailed session and object audit logging

---

## Naming & Tagging Convention

Each extension image tag follows this format:

```
<extension-name>:<pg_version>-<ext_version>-<timestamp>-<distro>
```

**Example:**
Building `pgvector` version `0.8.1` on PostgreSQL `17.6` for the `trixie`
distro, with build timestamp `202509101200`, results in:

```
pgvector:17.6-0.8.1-202509101200-trixie
```

For convenience, **rolling tags** should also be published:

```
pgvector:17.6-0.8.1-trixie
pgvector:17-0.8.1-trixie
```

This scheme ensures:

- Alignment with the upstream `postgres-containers` base images
- Explicit PostgreSQL and extension versioning
- Multi-distro support

---

## Roadmap / Open Questions

- Should each extension live in its **own dedicated folder**?
- Should each extension follow its **own release cycle**?
- Must every release pass **smoke tests** (e.g. via [Kind](https://kind.sigs.k8s.io/))?
- Should we define policies for:

  - Licensing (must be open source)?
  - Contribution and ownership
  - Governance aligned with the [CloudNativePG project](https://cloudnative-pg.io/)?
- Can contributors propose and maintain additional extensions?
- Should each extension have designated **component owners** responsible for
  maintenance, reviews, and release management?
