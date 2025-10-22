# pgaudit Extension

PostgreSQL Audit Extension for detailed session and object audit logging.

## Supported Versions

| PostgreSQL | pgaudit | Distros | Status |
|------------|---------|---------|--------|
| 18         | 18.0    | bookworm, trixie | ✅ Active |

## Usage

### PostgreSQL 18
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-with-pgaudit
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



## Available Images

- `ghcr.io/cloudnative-pg/pgaudit:18-18.0-bookworm`
- `ghcr.io/cloudnative-pg/pgaudit:18-18.0-trixie`

## Links

- [pgaudit Documentation](https://github.com/pgaudit/pgaudit)
- [CloudNativePG Extensions Guide](https://cloudnative-pg.io/documentation/current/imagevolume_extensions/)