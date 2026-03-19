# VectorChord

[VectorChord](https://github.com/tensorchord/VectorChord) is an open-source
extension for high-performance and disk-efficient vector similarity search in
PostgreSQL.

This image provides a convenient way to deploy and manage `vchord` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add pgvector and VectorChord extension images to your Cluster

`vchord` depends on `pgvector`, so both extensions must be configured in your
`Cluster` resource:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-vchord
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    shared_preload_libraries:
    - vchord
    extensions:
    - name: pgvector
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgvector
        reference: ghcr.io/cloudnative-pg/pgvector:0.8.1-18-trixie
    - name: vchord
      image:
        reference: ghcr.io/cloudnative-pg/vchord:1.1.1-18-trixie
```

### 2. Enable the extensions in a database

Create or update a `Database` resource and ensure `vector` is available before
`vchord`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-vchord-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-vchord
  extensions:
  - name: vector
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgvector
    version: '0.8.1'
  - name: vchord
    version: '1.1.1'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see both `vector` and `vchord` listed among installed extensions.
