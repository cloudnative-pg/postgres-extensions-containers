# pg_jsonschema

[pg_jsonschema](https://github.com/supabase/pg_jsonschema) is a PostgreSQL
extension that adds JSON Schema validation for `json` and `jsonb` data.

This image provides a convenient way to deploy and manage `pg_jsonschema` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the extension image to your Cluster

Define the `pg-jsonschema` extension under the `postgresql.extensions` section
of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-jsonschema
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-jsonschema
      image:
        # renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
        reference: ghcr.io/cloudnative-pg/pg-jsonschema:0.3.4-18-trixie
```

### 2. Enable the extension in a database

Create or update a `Database` resource to install the extension in a specific
database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pg-jsonschema-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pg-jsonschema
  extensions:
  - name: pg_jsonschema
    # renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
    version: "0.3.4"
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `pg_jsonschema` listed among the installed extensions.
