# pgAudit Extension

[pgAudit](https://github.com/pgaudit/pgaudit) is an open-source extension
that provides detailed session and/or object audit logging for PostgreSQL.

## Usage

### 1. Add the pgAudit extension image to your Cluster

Define the `pgaudit` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgaudit
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
      - "pgaudit"
    parameters:
      pgaudit.log: "all, -misc"
      pgaudit.log_catalog: "off"
      pgaudit.log_parameter: "on"
      pgaudit.log_relation: "on"

    extensions:
    - name: pgaudit
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgaudit
        reference: ghcr.io/cloudnative-pg/pgaudit:18.0-18-trixie
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
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgaudit
    version: '18.0'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pgaudit` listed among the installed extensions.
