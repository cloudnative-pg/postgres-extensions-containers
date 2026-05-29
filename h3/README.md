# H3
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[H3](https://github.com/postgis/h3-pg) is a PostgreSQL extension that provides
bindings for [H3](https://h3geo.org/), Uber's open-source **hierarchical
hexagonal geospatial indexing system**. It lets you index, aggregate, and
join location data on a grid of hexagonal cells directly in SQL.

This image provides a convenient way to deploy and manage the core `h3`
extension with [CloudNativePG](https://cloudnative-pg.io/).

> [!NOTE]
> The upstream `h3-pg` package also ships a companion `h3_postgis` extension
> that bridges H3 and PostGIS. This image bundles only the self-contained
> core `h3` extension; it does not include `h3_postgis`.

## Usage

### 1. Add the H3 extension image to your Cluster

Define the `h3` extension under the `postgresql.extensions` section of your
`Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-h3
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: h3
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-h3
        reference: ghcr.io/cloudnative-pg/h3:4.2.3-18-trixie
```

### 2. Enable the extension in a database

You can install `h3` in a specific database by creating or updating a
`Database` resource. For example, to enable it in the `app` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: cluster-h3-app
spec:
  name: app
  owner: app
  cluster:
    name: cluster-h3
  extensions:
  - name: h3
    # renovate: suite=trixie-pgdg depName=postgresql-18-h3 extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '4.2.3'
```

### 3. Verify installation

Once the database is ready, connect to it with `psql` and run:

```sql
\dx
```

You should see `h3` listed among the installed extensions. You can then try a
basic call, for example resolving a coordinate to an H3 cell at resolution 9:

```sql
SELECT h3_lat_lng_to_cell(POINT(-122.4194, 37.7749), 9);
```

## Contributors

This extension is maintained by:

- Jeff Mealo (@jmealo)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

The `h3-pg` bindings and the bundled `libh3` C library are both released
upstream under the Apache-2.0 license.

> [!IMPORTANT]
> The Debian `libh3-1` package ships a `copyright` file (bundled in this image
> under `/licenses/`) that classifies two upstream files — `README.md` and
> `src/h3lib/lib/coordijk.c` — as `AGPL-3+`, attributing them to DGGRID /
> Southern Oregon University. This appears to be an over-conservative Debian
> classification of an algorithm-origin credit: the current upstream
> ([uber/h3](https://github.com/uber/h3)) carries Apache-2.0 headers on those
> files and contains no AGPL license text. Because `coordijk.c` is compiled
> into the bundled `libh3.so.1`, this is surfaced here for maintainer review.

All relevant license and copyright information for the `h3` extension and its
dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
