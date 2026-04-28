# pglinter

[pglinter](https://github.com/pmpetit/pglinter) is an open-source extension
that checks **database design** in PostgreSQL.

This image provides a convenient way to deploy and manage `pglinter` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the pglinter extension image to your Cluster

Define the `pglinter` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pglinter
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pglinter
      image:
        reference: ghcr.io/cloudnative-pg/pglinter:2.0.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pglinter` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pglinter-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pglinter
  extensions:
  - name: pglinter
    version: '2.0.0'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pglinter` listed among the installed extensions.
