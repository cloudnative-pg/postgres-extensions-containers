# pg\_partman

[pg\_partman](https://github.com/pgpartman/pg_partman) is an open-source extension
that enables **automatic partition management** in PostgreSQL.

This image provides a convenient way to deploy and manage `pg_partman` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the pg\_partman extension image to your Cluster

Define the `pg_partman` extension under the `postgresql.extensions` section of
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
    - name: pg_partman
      image:
        reference: ghcr.io/cloudnative-pg/pg_partman:5.3.1-2-trixie
```

### 2. Enable the extension in a database

You can install `pg_partman` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg_partman-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg_partman
  extensions:
  - name: pg_partman
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_partman` listed among the installed extensions.
