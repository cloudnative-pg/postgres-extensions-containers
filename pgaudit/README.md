# pgaudit Extension

PostgreSQL Audit Extension for detailed session and object audit logging.

## Supported Versions

| PostgreSQL | pgaudit | Distros | Status |
|------------|---------|---------|--------|
| 18         | 18.0    | bookworm, trixie | ✅ Active |

## Usage

### 1. Add the PgVector extension image to your Cluster

Define the `pgaudit` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

### PostgreSQL 18
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgaudit
spec:
  instances: 3
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-bookworm
  postgresql:
    extensions:
      - name: pgaudit
        image:
          reference: ghcr.io/cloudnative-pg/pgaudit:18-18.0-bookworm
    parameters:
      shared_preload_libraries: "pgaudit"
      pgaudit.log: "all"
  storage:
    size: 1Gi
```

### 2. Enable the extension in a database

You can install `pgaudit` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgaudit-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgaudit
  extensions:
  - name: pgaudit
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pgaudit` listed among the installed extensions.


## Available Images

- `ghcr.io/cloudnative-pg/pgaudit:18-18.0-bookworm`
- `ghcr.io/cloudnative-pg/pgaudit:18-18.0-trixie`

## Links

- [pgaudit Documentation](https://github.com/pgaudit/pgaudit)
- [CloudNativePG Extensions Guide](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/)