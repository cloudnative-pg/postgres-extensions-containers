# pg_qualstats
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[pg_qualstats](https://github.com/powa-team/pg_qualstats) is a PostgreSQL
extension that collects statistics about predicates (quals) found in
`WHERE` clauses and `JOIN` conditions. It can be used to identify missing
indexes and understand query workload patterns. For more information, see the
[official documentation](https://powa.readthedocs.io/en/latest/components/pg_qualstats.html).

## Usage

The `pg_qualstats` extension must be loaded via `shared_preload_libraries`
to hook into the query executor and collect predicate statistics.

### 1. Add the pg_qualstats extension image to your Cluster

Define the `pg-qualstats` extension under the `postgresql.extensions` section
of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-qualstats
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
    - pg_qualstats
    extensions:
    - name: pg-qualstats
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg-qualstats
        reference: ghcr.io/cloudnative-pg/pg-qualstats:2.1.3-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_qualstats` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-qualstats-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-qualstats
  extensions:
  - name: pg_qualstats
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-qualstats
    version: '2.1.3'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_qualstats` listed among the installed extensions.

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

All relevant license and copyright information for the `pg_qualstats` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
