# PgVector

[PgVector](https://github.com/pgvector/pgvector) is an open-source vector similarity search for PostgreSQL.

## How It Works

To use this extension container image, first add it to your Cluster.
For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgvector
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
      - name: pgvector
        image:
          reference: ghcr.io/cloudnative-pg/pgvector:0.8.1-18-trixie
```

Then, create or add it to an existing Database object to install the extension in a target database.
For example, to add it to the `app` Database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgvector-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgvector
  extensions:
  - name: vector
```
