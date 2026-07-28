# pgRouting

[pgRouting](https://pgrouting.org/) extends the [PostGIS](https://postgis.net/)/PostgreSQL geospatial database to provide geospatial routing and other network analysis functionality.

This image provides a convenient way to deploy and manage `pgRouting` with [CloudNativePG](https://cloudnative-pg.io/).

> [!NOTE]
> `pgRouting` depends on `PostGIS`. When deploying `pgRouting`, you must also include the `postgis` extension image in your Cluster definition.

## Usage

### 1. Add the pgRouting and PostGIS extension images to your Cluster

Define the `postgis` and `pgrouting` extensions under the `postgresql.extensions` section of your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pgrouting
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: postgis
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
        reference: ghcr.io/cloudnative-pg/postgis-extension:3.6.4-18-trixie
      ld_library_path:
      - system
      env:
      - name: GDAL_DATA
        value: ${image_root}/share/gdal
      - name: PROJ_DATA
        value: ${image_root}/share/proj
    - name: pgrouting
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pgrouting
        reference: ghcr.io/cloudnative-pg/pgrouting:4.0.1-18-trixie
      ld_library_path:
      - system
```

### 2. Enable the extension in a database

You can install `pgrouting` in a specific database by creating or updating a `Database` resource. Note that `postgis` must be listed before `pgrouting`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-pgrouting-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-pgrouting
  extensions:
  - name: postgis
    # renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3 extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '3.6.4'
  - name: pgrouting
    # renovate: suite=trixie-pgdg depName=postgresql-18-pgrouting extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '4.0.1'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `postgis` and `pgrouting` listed among the installed extensions.
