# TDS-FDW

[TDS-FDW](https://github.com/tds-fdw/tds-fdw/) is a PostgreSQL foreign data
wrapper to connect to TDS databases (Sybase and Microsoft SQL Server).

This image provides a convenient way to deploy and manage `tds-fdw` with
[CloudNativePG](https://cloudnative-pg.io/).

## Usage

### 1. Add the tds-fdw extension image to your Cluster

Define the `tds-fdw` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-tds-fdw
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: tds-fdw
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-tds-fdw
        reference: ghcr.io/cloudnative-pg/tds-fdw-extension:3.6.2-18-trixie
      ld_library_path:
      - system
      # Requires CloudNativePG 1.29 (or higher)
      env:
      - name: GDAL_DATA
        value: ${image_root}/share/gdal
      - name: PROJ_DATA
        value: ${image_root}/share/proj
```

### 2. Enable the extension in a database

You can install `tds-fdw` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-tds-fdw-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-tds-fdw
  extensions:
  - name: tds-fdw
    # renovate: suite=trixie-pgdg depName=postgresql-18-tds-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '2.0.5'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `tds_fdw` listed among the installed extensions.


### 4. Verify OS dependencies are properly satisfied

TDS-FDW requires several OS dependencies that are being provided via the `system` directory.
CloudNativePG makes them available to PostgreSQL by adding the directory to LD_LIBRARY_PATH for the PostgreSQL process.

To verify that all tds_fdw shared libraries requirements are being properly satisfied,
connect to the container and run:

```bash
cd /extensions/tds_fdw/lib
LD_LIBRARY_PATH=/extensions/tds_fdw/system ldd tds_fdw*
```

Make sure there are no missing shared libraries.
