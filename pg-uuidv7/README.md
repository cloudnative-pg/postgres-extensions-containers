# PG-UUIDv7

[PG-UUIDv7](https://github.com/pg-uuidv7/pg-uuidv7) is a tiny Postgres extension
to create valid version 7 UUIDs in PostgresQL.

This image provides a convenient way to deploy and manage `pg-uuidv7` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the pg-uuidv7 extension image to your Cluster

Define the `pg-uuidv7` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-uuidv7
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-uuidv7
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg-uuidv7
        reference: ghcr.io/cloudnative-pg/pg-uuidv7:0.8.2-18-trixie
```

### 2. Enable the extension in a database

You can install `pg-uuidv7` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-uuidv7-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-uuidv7
  extensions:
  - name: pg_uuidv7
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg-uuidv7 extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '0.8.2'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_uuidv7` listed among the installed extensions.
