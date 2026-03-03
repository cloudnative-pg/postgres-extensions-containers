# Pg-Crash
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

<!--
TODO: Replace this section with a brief introduction of your extension.
Describe what the extension does and what it is useful for.
Add a reference to the official documentation if available.
-->

The pg-crash PostgreSQL extension provides [describe the main functionality
here]. For more information, see the [official documentation](https://example.com).

## Usage

<!--
Usage: add instructions on how to use the extension with CloudNativePG.
Include code snippets for Cluster and Database resources as needed.
-->

### Add the pg-crash extension image to your Cluster

Define the `pg-crash` extension under the `postgresql.extensions` section of
your `Cluster` resource. For example:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-crash
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 1

  storage:
    size: 1Gi

  postgresql:
    extensions:
    - name: pg-crash
      image:
        # renovate: suite=trixie-pgdg depName=postgresql-18-pg-crash
        reference: ghcr.io/cloudnative-pg/pg-crash:0.3-18-trixie
    shared_preload_libraries:
    - pg_crash
    parameters:
      # See https://www.postgresql.org/docs/current/server-shutdown.html
      # SIGHUP  (1)  - Reload
      # SIGINT  (2)  - Fast shutdown
      # SIGQUIT (3)  - Immediate shutdown
      # SIGTERM (15) - Smart shutdown
      crash.signals: '1 2 3 15'
      crash.delay: '60'
```

## Contributors

This extension is maintained by:

- FirstName LastName (@GitHub_Handle)

The maintainers are responsible for:

- Monitoring upstream releases and security vulnerabilities.
- Ensuring compatibility with supported PostgreSQL versions.
- Reviewing and merging contributions specific to this extension's container
  image and lifecycle.

---

## Licenses and Copyright

This container image contains software that may be licensed under various
open-source licenses.

All relevant license and copyright information for the `pg-crash` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
