# wal2json
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[wal2json](https://github.com/eulerto/wal2json) is a PostgreSQL **logical
decoding output plugin**. It reads the write-ahead log (WAL) of a database via
a logical replication slot and emits the changes as JSON, which makes it a
common building block for change data capture (CDC) pipelines (e.g. Debezium,
custom replication tooling, or audit streams).

Because `wal2json` is a logical decoding output plugin rather than a regular
extension, it does **not** expose a `CREATE EXTENSION` object. The plugin is
loaded on demand by PostgreSQL when a replication slot is created with the
`wal2json` output plugin.

This image provides a convenient way to deploy and manage `wal2json` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the wal2json extension image to your Cluster

Define the `wal2json` extension under the `postgresql.extensions` section of
your `Cluster` resource. Logical decoding requires `wal_level` to be set to
`logical`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-wal2json
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    parameters:
      wal_level: logical
    extensions:
    - name: wal2json
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-wal2json
        reference: ghcr.io/cloudnative-pg/wal2json:2.6-18-trixie
```

> [!NOTE]
> Unlike most extensions, `wal2json` is a logical decoding output plugin and
> does not require a `Database` resource with `CREATE EXTENSION`. The plugin
> is referenced directly when a logical replication slot is created.

### 2. Create a logical replication slot using `wal2json`

Once the cluster is ready, connect to the database with `psql` and create a
logical replication slot that uses the `wal2json` output plugin:

```sql
SELECT * FROM pg_create_logical_replication_slot('wal2json_slot', 'wal2json');
```

Some applications (for example, Teleport), may do this automatically.

### 3. Verify installation

Consume changes from the slot to confirm the plugin is loaded correctly. After
producing some activity (e.g. `CREATE TABLE t (id int); INSERT INTO t VALUES
(1);`), peek at the slot:

```sql
SELECT data
FROM pg_logical_slot_peek_changes('wal2json_slot', NULL, NULL);
```

You should see the changes emitted as JSON documents.

When you are done, drop the slot to release resources:

```sql
SELECT pg_drop_replication_slot('wal2json_slot');
```

## Contributors

This extension is maintained by:

- FirstName LastName (@GitHub_Handle)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

`wal2json`:

- **Copyright:** (c) 2013-2018 Euler Taveira de Oliveira
- **License:** BSD 3-Clause License

All relevant license and copyright information for the `wal2json` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
