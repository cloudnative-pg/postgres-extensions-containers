# First-Last-Agg

[First-Last-Agg](https://github.com/wulczer/first_last_agg) is a simple
extension providing two aggregate functions, last and first aggregate
functions, operating on any element type and returning the last or the first
value of the group.

This image provides a convenient way to deploy and manage `first_last_agg` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the first_last_agg extension image to your Cluster

Define the `first_last_agg` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-first-last-agg
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: first_last_agg
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-first-last-agg
        reference: ghcr.io/cloudnative-pg/first-last-agg:0.8.2-18-trixie
```

### 2. Enable the extension in a database

You can install `first_last_agg` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-first-last-agg-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-first-last-agg
  extensions:
  - name: first_last_agg
    # renovate: suite=trixie-pgdg depName=postgresql-18-first-last-agg extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '0.8.2'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `first_last_agg` listed among the installed extensions.
