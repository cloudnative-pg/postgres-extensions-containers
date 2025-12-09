# pg_ivm Extension

[pg_ivm](https://github.com/sraoss/pg_ivm) is an open-source extension
that provides **Incremental View Maintenance (IVM)** for PostgreSQL, allowing
materialized views to be updated incrementally when base tables change.

## Usage

### 1. Add the pg_ivm extension image to your Cluster

Define the `pg_ivm` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-ivm
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
      - "pg_ivm"
  postgresql:
    extensions:
    - name: pg_ivm
      image:
        reference: ghcr.io/cloudnative-pg/pg_ivm:1.13-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_ivm` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-ivm-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-ivm
  extensions:
  - name: pg_ivm
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_ivm` listed among the installed extensions.
