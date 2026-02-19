# TimescaleDB (Apache 2.0 Edition)

[TimescaleDB](https://github.com/timescale/timescaledb) is an open-source
time-series database built on PostgreSQL. It enables fast analytics, efficient
storage, and powerful querying for time-series workloads.

> [!NOTE]
> This image contains only the Apache 2.0 licensed components of TimescaleDB
> (known as "TimescaleDB Apache-2 Edition") to ensure CNCF licensing
> compliance. Advanced features requiring the Timescale License (TSL) are not
> included.

This image provides a convenient way to deploy and manage the open-source core
of TimescaleDB with [CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the TimescaleDB extension image to your Cluster

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
        reference: ghcr.io/cloudnative-pg/timescaledb-oss:2.24.0-18-trixie
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
    version: '2.24.0'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `timescaledb` listed among the installed extensions.

### 4. Create a hypertable

To use TimescaleDB's time-series features, create a hypertable:

```sql
-- Create a regular table
CREATE TABLE sensor_data (
  time TIMESTAMPTZ NOT NULL,
  sensor_id INTEGER,
  temperature DOUBLE PRECISION,
  humidity DOUBLE PRECISION
);

-- Convert it to a hypertable
SELECT create_hypertable('sensor_data', 'time');

-- Insert some data
INSERT INTO sensor_data VALUES (NOW(), 1, 21.5, 45.0);
```

## Maintainers

This container image is maintained by @shuusan.

## License

This image contains only the Apache 2.0 licensed components of TimescaleDB.
Features requiring the Timescale License (TSL) are not included to ensure
compliance with CNCF licensing requirements.

All relevant license and copyright information for the `timescaledb-oss` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.

For further information, refer to
[Software Licensing: Timescale License (TSL)](https://www.tigerdata.com/legal/licenses).
