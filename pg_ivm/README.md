# pg_ivm

[pg_ivm](https://github.com/sraoss/pg_ivm) is an open-source extension
that provides **Incremental View Maintenance (IVM)** for PostgreSQL, allowing
materialized views to be updated incrementally when base tables change.

## Usage

<!--
Usage: add instructions on how to use the extension with CloudNativePG.
Include code snippets for Cluster and Database resources as needed.
-->

### 1. Add the pg_ivm extension image to your Cluster

Define the `pg_ivm` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg_ivm
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg_ivm
      image:
        reference: ghcr.io/cloudnative-pg/pg_ivm:1.0-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_ivm` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg_ivm-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg_ivm
  extensions:
  - name: pg_ivm
    version: '1.13'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_ivm` listed among the installed extensions.

## Maintainers

This container image is maintained by @shuusan.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_ivm` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
