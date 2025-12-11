[![CloudNativePG](./logo/cloudnativepg.png)](https://cloudnative-pg.io/)

# CNPG PostgreSQL Extensions Container Images

This repository provides **maintenance scripts** for building **immutable
container images** containing PostgreSQL extensions supported by
[CloudNativePG](https://cloudnative-pg.io/). These images are designed to
integrate seamlessly with the [`image volume extensions` feature](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/)
in CloudNativePG.

For detailed instructions on building the images, see the [`BUILD.md` file](BUILD.md).

---

## Requirements

- **CloudNativePG** ≥ 1.27
- **PostgreSQL** ≥ 18 (requires the `extension_control_path` feature)
- **Kubernetes** 1.33+ (with [ImageVolume feature enabled in 1.33 and 1.34](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/))

---

## Supported Extensions

CloudNativePG actively maintains the following third-party extensions, provided
they are maintained by their respective authors, and PostgreSQL Debian Group
(PGDG) packages are available.

| Extension | Description | Project URL |
| :--- | :--- | :--- |
| **[pgAudit](pgaudit)** | PostgreSQL audit extension | [https://github.com/pgaudit/pgaudit](https://github.com/pgaudit/pgaudit) |
| **[pgvector](pgvector)** | Vector similarity search for PostgreSQL | [https://github.com/pgvector/pgvector](https://github.com/pgvector/pgvector) |
| **[PostGIS](postgis)** | Geospatial database extension for PostgreSQL | [https://postgis.net/](https://postgis.net/) |
| **[Timescaledb](timescaledb)** | Time-series database for PostgreSQL | [https://github.com/timescale/timescaledb/](https://github.com/timescale/timescaledb/) |


Extensions are provided only for the OS versions already built by the
[`cloudnative-pg/postgres-containers`](https://github.com/cloudnative-pg/postgres-containers) project,
specifically Debian `stable` and `oldstable`.

---

## Contribution and Maintenance Policy

Contributors are welcome to propose and maintain additional extensions.

### Governance and Compliance

The project adheres to the following frameworks:

- **Governance Model:** complies with the CloudNativePG (CNPG) Governance
  Model, as defined in [`GOVERNANCE.md`](GOVERNANCE.md).
- **Code of Conduct:** follows the CNCF Code of Conduct, as defined in
  [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

### Extension Requirements

When proposing a new extension, the following criteria must be met:

- **Licensing and IP ownership:** the extension's licensing must be compatible
  with the project's goals. We approve all licences that are on the CNCF
  Allowed Third-Party Licence Policy list (see
  [CNCF Allowed Licence Policy](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md#cncf-allowlist-license-policy)).
- **Structure:** only one extension can be included within an extension folder.
- **Debian Packages:** Extension images must be built using a Debian package
  provided by a trusted source like the
  [PostgreSQL Global Development Group (PGDG)](https://wiki.postgresql.org/wiki/Apt).
  This ensures compatibility with the base images and standard package
  management procedures.
- **Licence inclusion:** all necessary licence agreements for the extension and
  its dependencies must be included within the extension folder (refer to the
  examples in the `pgvector` and `postgis` folders).

### Submission Process

1. **Request and commitment:** Open a new issue requesting the extension.
   The contributor(s) must agree to become "component owners" and maintainers
   for that extension.
2. **Approval:** Once approved by maintainers, the component owner(s) will be
   added to the `CODEOWNERS` file for the specific folder.
3. **Submission:** Component owner(s) open a Pull Request (PR) to introduce the
   new extension. The PR is reviewed, approved, and merged.
4. **Naming:** The name of the extension is the registry name.

### Removal Policy

If component owners decide to stop maintaining their extension, and no other
contributors are found, the main project maintainers reserve the right to
**unconditionally remove that extension**.

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

## Image Labels

Each extension image includes OCI-compliant labels for runtime inspection
and tooling integration. These metadata fields enable CloudNativePG and
other tools to identify the base PostgreSQL version and OS distribution.

### CloudNativePG-Specific Labels

| Label | Description | Example |
| :--- | :--- | :--- |
| `io.cloudnativepg.image.base.name` | Base PostgreSQL container image | `ghcr.io/cloudnative-pg/postgresql:18-minimal-bookworm` |
| `io.cloudnativepg.image.base.pgmajor` | PostgreSQL major version | `18` |
| `io.cloudnativepg.image.base.os` | Operating system distribution | `bookworm` |

### Standard OCI Labels

In addition to CloudNativePG-specific labels, all images include standard OCI
annotations as defined by the [OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/annotations.md):

| Label | Description |
| :--- | :--- |
| `org.opencontainers.image.created` | Image creation timestamp |
| `org.opencontainers.image.version` | Extension version |
| `org.opencontainers.image.revision` | Git commit SHA |
| `org.opencontainers.image.title` | Human-readable image title |
| `org.opencontainers.image.description` | Image description |
| `org.opencontainers.image.source` | Source repository URL |
| `org.opencontainers.image.licenses` | License identifier (Apache-2.0) |

You can inspect these labels using container tools:

```bash
# Using docker buildx imagetools
docker buildx imagetools inspect <image> --raw | jq '.annotations'

# Using skopeo
skopeo inspect docker://<image> | jq '.Labels'
```
