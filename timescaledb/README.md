# TimescaleDB (Apache 2.0 Edition) with CloudNativePG

[TimescaleDB](https://github.com/timescale/timescaledb) is the leading open-source time-series database, built on PostgreSQL. It enables fast analytics, efficient storage, and powerful querying for time-series workloads.

**Note**: This image contains only the Apache 2.0 licensed components of TimescaleDB to ensure CNCF licensing compliance. Advanced features requiring the Timescale License (TSL) are not included.

This image provides a convenient way to deploy and manage the open-source core of `TimescaleDB` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the timescaledb extension image to your Cluster

Define the `timescaledb` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-timescaledb
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
      - "timescaledb"
    parameters:
      timescaledb.telemetry_level: 'off'
      max_locks_per_transaction: '128'

    extensions:
    - name: timescaledb
      image:
        reference: ghcr.io/cloudnative-pg/timescaledb:2.23.1-18-trixie
```

### 2. Enable the extension in a database

You can install `timescaledb` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-timescaledb-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-timescaledb
  extensions:
  - name: timescaledb
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `timescaledb` listed among the installed extensions.
