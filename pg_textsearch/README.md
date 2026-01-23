# PgTextsearch


[pg_textsearch](https://github.com/timescale/pg_textsearch) is an extension that adds
**ranked full-text search (BM25)** to PostgreSQL.

## Usage

### 1. Add the pg_textsearch extension image to your Cluster

Define the `pg_textsearch` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg_textsearch
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg_textsearch
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg_textsearch
        reference: ghcr.io/cloudnative-pg/pg_textsearch:0.4.1-18-trixie
```

### 2. Enable the extension in a database

You can install `pg_textsearch` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg_textsearch-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg_textsearch
  extensions:
  - name: pg_textsearch
    # renovate: suite=trixie-pgdg depName=postgresql-18-pg_textsearch
    version: '0.4.1'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_textsearch` listed among the installed extensions.

## Contributors

This extension is maintained by:

- Bryan Wong (@ImSingee)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg_textsearch` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
