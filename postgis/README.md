# PostGIS

[PostGIS](https://postgis.net/) is an open-source geospatial database extension for PostgreSQL.

This image provides a convenient way to deploy and manage `PostGIS` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the PostGIS extension image to your Cluster

Define the `PostGIS` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-postgis
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
        reference: ghcr.io/cloudnative-pg/postgis-extension:3.6.2-18-trixie
      ld_library_path:
      - system
```

### 2. Enable the extension in a database

You can install `PostGIS` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-postgis-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-postgis
  extensions:
  - name: postgis
    # renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
    version: '3.6.2'
  - name: postgis_raster
  - name: postgis_sfcgal
  - name: fuzzystrmatch
  - name: address_standardizer
  - name: address_standardizer_data_us
  - name: postgis_tiger_geocoder
  - name: postgis_topology
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `postgis`, `postgis_raster` (and so on) listed among the installed extensions.


### 4. Verify OS dependencies are properly satisfied

PostGIS requires several OS dependencies that are being provided via the `system` directory.
CloudNativePG makes them available to PostgreSQL by adding the directory to LD_LIBRARY_PATH for the PostgreSQL process.

To verify that all PostGIS shared libraries requirements are being properly satisfied,
connect to the container and run:

```bash
cd /extensions/postgis/lib
LD_LIBRARY_PATH=/extensions/postgis/system ldd address_standardizer* postgis*
```

Make sure there are no missing shared libraries.
