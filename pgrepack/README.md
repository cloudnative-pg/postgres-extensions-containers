# Pg_repack
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

The pg_repack PostgreSQL extension provides a binary tool that can perform online operation that can remove bloat from tables and indexes. For more information, see the [official documentation](https://reorg.github.io/pg_repack/).

## Usage

A typical usage involves first installing the extension

```sql
CREATE EXTENSION pg_repack;
```

and then invoking the command-line tool. For example, to repack a bloated table called orders in the mydb database while keeping it fully accessible, you would run:

```shell
pg_repack -h localhost -U postgres -d mydb -t orders
```

To also reorder the table data along a specific index (e.g., orders_created_at_idx) for better read performance, you would use:

```shell
pg_repack -h localhost -U postgres -d mydb -t orders --order-by created_at
```

For a full-database repack targeting all eligible tables, simply omit the -t flag: pg_repack -d mydb. It is important to ensure that the target tables have a primary key or a unique, non-null index, as pg_repack requires one to correctly track row-level changes during the copy phase. Overall, pg_repack is an indispensable tool for DBAs managing large, write-heavy PostgreSQL databases where table bloat accumulates over time and downtime is not an option.

### 1. Add the pg_repack extension image to your Cluster

Define the `pg_repack` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg_repack
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg_repack
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg_repack
        reference: ghcr.io/cloudnative-pg/pg_repack:1.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_repack` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg_repack-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg_repack
  extensions:
  - name: pg_repack
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg_repack extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '1.0'
```

<!--
TODO: Adjust the extractVersion regex pattern above based on your extension's versioning scheme
Examples: \d+\.\d+ for major.minor (e.g., "18.0"), \d+\.\d+\.\d+ for major.minor.patch (e.g., "0.8.2")
-->

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_repack` listed among the installed extensions.

## Contributors

This extension is maintained by:

- Thomas Boussekey (@thomasboussekey)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_repack` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
