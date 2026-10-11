# PostgreSQL Anonymizer
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

The [PostgreSQL Anonymizer](https://gitlab.com/dalibo/postgresql_anonymizer) (or
`anon`) is an extension to mask or replace [personally identifiable information] (PII) or
commercially sensitive data from a Postgres database. For more information, see the [official documentation](https://postgresql-anonymizer.readthedocs.io).

## Usage

### 1. Add the PostgreSQL Anonymizer extension image to your Cluster

Define the PostgreSQL Anonymizer extension `anon` under the
`postgresql.extensions` section of your `Cluster` resource.

For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-postgresql-anonymizer
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: anon
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-postgresql-anonymizer
        reference: ghcr.io/cloudnative-pg/postgresql_anonymizer:3.2.2-18-trixie
```

### 2. Enable the extension in a database

You can install PostgreSQL Anonymizer extension `anon` in a specific database by
creating or updating a `Database` resource. For example, to enable it in a
`db` database:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Database
metadata:
  name: database-postgresql-anonymizer
spec:
  name: db
  owner: app
  cluster:
    name: cluster-postgresql-anonymizer
  extensions:
  - name: anon
  # renovate: suite=trixie-pgdg depName=postgresql-18-postgresql-anonymizer extractVersion=^(?<version>\d+\.\d+\.\d+)
    version: '3.2.2'
```

On top of the creation, it's recommended to load the extension in the `db` database.
This can be done with this command :

```sql
ALTER DATABASE db SET session_preload_libraries = 'anon';
```

The setting will be applied for the next sessions.
You need to reconnect to the database for the change to visible.

### 3. Initialize the extension

After reconnection, you can initialize the extension with the `anon.init()` function :

```sql
db=# SELECT anon.init('/extensions/anon/share/extension/');
 init 
------
 t
(1 row)
```

### 4. Verify installation

Once the `db` database is ready, connect to it with `psql -d db` and run :

```sql
SELECT * FROM pg_extension WHERE extname = 'anon';
```

```sql
db=# SELECT * FROM pg_extension WHERE extname = 'anon';
  oid  | extname | extowner | extnamespace | extrelocatable | extversion | extconfig | extcondition 
-------+---------+----------+--------------+----------------+------------+-----------+--------------
 16394 | anon    |       10 |         2200 | f              | 3.2.2      |           | 
(1 row)
```

If the result is empty, the extension is not declared in your database.

Finally, look at the state of the extension with :

```sql
SELECT anon.is_initialized();
```

```console
db=# SELECT anon.is_initialized();
 is_initialized 
----------------
 t
(1 row)
```

If the result is not `t`, the extension's data is not present.

## Contributors

This extension is maintained by:

- Damien Clochard (@daamien)
- Pierrick Chovelon (@pchovelon)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

The PostgreSQL License
===============================================================================

Copyright (c) 2018-2026, DALIBO SCOP

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose, without fee, and without a written agreement
is hereby granted, provided that the above copyright notice and this paragraph
and the following two paragraphs appear in all copies.

IN NO EVENT SHALL DALIBO SCOP BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING
OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF DALIBO SCOP
HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

DALIBO SCOP SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND DALIBO SCOP HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT,
UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
