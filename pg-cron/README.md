# pg_cron
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[pg_cron](https://github.com/citusdata/pg_cron) is an open-source extension
that provides a simple cron-based job scheduler for PostgreSQL, allowing you
to schedule PostgreSQL commands directly from the database.

## Usage

### 1. Add the cron extension image to your Cluster

Define the `pg_cron` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-cron
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    parameters:
      cron.database_name: app
      cron.use_background_workers: "on"

    shared_preload_libraries:
    - "pg_cron"

    extensions:
    - name: pg_cron
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-cron
        reference: ghcr.io/cloudnative-pg/pg-cron:1.6.7-18-trixie
```

### 2. Enable the extension in a database

You can install `cron` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-cron-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-cron
  extensions:
  - name: pg_cron
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_cron` listed among the installed extensions.

## Contributors

This extension is maintained by:

- Jeremy Schneider (@ardentperf)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_cron` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
