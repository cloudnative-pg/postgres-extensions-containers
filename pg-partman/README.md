# pg_partman
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[pg_partman](https://github.com/pgpartman/pg_partman) is a PostgreSQL extension
for automated table partition management. It supports both time-based and
ID-based partitioning with automatic creation and maintenance of child tables.

The extension includes a background worker (`pg_partman_bgw`) that can
automatically run partition maintenance at configured intervals, removing the
need for external cron jobs.

For more information, see the
[official documentation](https://github.com/pgpartman/pg_partman).

## Usage

The `pg_partman` extension must be loaded via `shared_preload_libraries` to
enable the background worker. The worker periodically runs
`partman.run_maintenance_proc()` to create new partitions and drop expired ones.

### 1. Add the pg_partman extension image to your Cluster

Define the `pg-partman` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-partman
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
    - pg_partman_bgw
    extensions:
    - name: pg-partman
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-partman
        reference: ghcr.io/cloudnative-pg/pg-partman:5.4.3-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_partman` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-partman-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-partman
  extensions:
  - name: pg_partman
    # renovate: suite=trixie-pgdg depName=postgresql-18-partman
    version: '5.4.3'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_partman` listed among the installed extensions.

## Included utilities

This image also bundles the following Python maintenance scripts in `/bin/`:

- `check_unique_constraint.py` — validates unique constraints across partitions
- `dump_partition.py` — exports individual partitions for archival
- `vacuum_maintenance.py` — targeted vacuum operations on partitioned tables

> [!NOTE]
> These scripts require a Python 3 runtime and the `psycopg2` library, which
> are not included in the minimal base image. They are provided for
> environments where Python is available on the host or in a sidecar container.

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

All relevant license and copyright information for the `pg_partman` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
