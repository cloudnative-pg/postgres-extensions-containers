# pg_oidc_validator
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[pg_oidc_validator](https://github.com/percona/pg_oidc_validator) is an
experimental OAuth validator library for PostgreSQL 18, developed by Percona.
It validates JWT access tokens issued by OIDC providers, enabling native OAuth
authentication via `pg_hba.conf`. It supports most providers that implement
OIDC and return a valid JWT as an access token, including Keycloak and
Microsoft Entra ID. For more information, see the
[official documentation](https://github.com/percona/pg_oidc_validator#readme).

> [!WARNING]
> **This library is still experimental and not intended for production use.**
> It is built from pre-compiled `.deb` packages published on GitHub (not from
> PGDG) and is only available for the `linux/amd64` platform. There is no
> `arm64` build available at this time.

## Usage

The `pg_oidc_validator` extension is **not** a `CREATE EXTENSION` module.
It is an OAuth validator library loaded via the `oauth_validator_libraries`
PostgreSQL configuration parameter.

### 1. Add the pg-oidc-validator extension image to your Cluster

Define the `pg-oidc-validator` extension under the `postgresql.extensions`
section of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-oidc-validator
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    parameters:
      oauth_validator_libraries: pg_oidc_validator
    extensions:
    - name: pg-oidc-validator
      image:
        reference: ghcr.io/cloudnative-pg/pg-oidc-validator:0.2-18-trixie
    pg_hba:
    - host all all 0.0.0.0/0 oauth scope="openid",issuer=https://your-oidc-issuer
```

### 2. Verify installation

Once the cluster is ready, connect to it and check the library is loaded:

```sql
SHOW oauth_validator_libraries;
```

You should see `pg_oidc_validator` in the output.

## System library dependencies

This extension depends on `libcurl` and its transitive dependencies for
making HTTPS calls to OIDC providers. These system libraries are bundled
automatically during the image build and placed under `/system/`.

## Contributors

This extension is maintained by:

- Erling Kristiansen (@egkristi)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

The `pg_oidc_validator` library is licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

All relevant license and copyright information for bundled system library
dependencies are included within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
