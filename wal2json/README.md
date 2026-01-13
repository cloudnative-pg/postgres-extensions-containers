# wal2json

[wal2json](https://github.com/eulerto/wal2json) is an open-source logical decoding
output plugin for PostgreSQL that converts WAL (Write-Ahead Log) changes to JSON format.

This image provides a convenient way to deploy and manage `wal2json` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the wal2json plugin image to your Cluster

Define the `wal2json` plugin under the `postgresql.extensions` section of
your `Cluster` resource. For example:

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

### 2. Configure logical replication

To use `wal2json`, you need to:

1. Set `wal_level` to `logical` in your PostgreSQL configuration (as shown above)
2. Create a logical replication slot using the `wal2json` output plugin

Connect to your database and create a replication slot:

```sql
SELECT * FROM pg_create_logical_replication_slot('wal2json_slot', 'wal2json');
```

### 3. Use the replication slot

You can now use the replication slot to stream changes in JSON format. For example,
using `pg_recvlogical`:

```bash
pg_recvlogical -d your_database -h your_host -U your_user \
  --slot wal2json_slot --start -f -
```

### 4. Verify installation

To verify that `wal2json` is available, you can check the available output plugins:

```sql
SELECT * FROM pg_available_logical_replication_slots;
```

Or check if the library is loaded:

```sql
SELECT * FROM pg_show_replication_slots();
```
