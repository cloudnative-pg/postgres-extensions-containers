# PgVector

[PgVector](https://github.com/pgvector/pgvector) is an open-source extension
that enables **vector similarity search** in PostgreSQL.

This image provides a convenient way to deploy and manage `pgvector` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the PgVector extension image to your Cluster

Define the `pgvector` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

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

### 2. Enable the extension in a database

You can install `pgvector` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

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
    version: '0.8.1'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `vector` listed among the installed extensions.
