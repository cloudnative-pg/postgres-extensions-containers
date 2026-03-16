# `pg_crash`
<!--
SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
SPDX-License-Identifier: Apache-2.0
-->

[pg_crash](https://github.com/cybertec-postgresql/pg_crash) is a PostgreSQL
extension designed for **fault injection** and **chaos engineering**. It allows
administrators to simulate various failure scenarios—such as backend crashes
and signal handling issues—to verify the resilience of High Availability (HA)
clusters and self-healing mechanisms.

> [!CAUTION]
> **DO NOT USE THIS IMAGE IN PRODUCTION.**
> This extension is designed to intentionally destabilize and terminate
> PostgreSQL processes. Deploying it in production will cause service downtime
> and potential data availability issues.
>
> Only deploy this extension in **dedicated test or staging namespaces**.
> Consider using Kubernetes admission controllers or OPA/Gatekeeper policies
> to prevent accidental deployment to production clusters.

This extension image is maintained by the CNPG project and supersedes the
[`pgcrash-containers` project](https://github.com/cloudnative-pg/pgcrash-containers).

## Usage

The `pg_crash` extension must be loaded via `shared_preload_libraries`. It
operates by periodically sending random signals (selected from a user-defined
list) to PostgreSQL backend processes.

The following example configures a cluster to experience "Chaos" by randomly
sending signals every 60 seconds. This is ideal for testing how quickly
CloudNativePG detects a failure and promotes a new primary.

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: cluster-pg-crash
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
  instances: 3

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
      log_min_messages: 'DEBUG1'
      # See https://www.postgresql.org/docs/current/server-shutdown.html
      # SIGHUP  (1)  - Reload
      # SIGINT  (2)  - Fast shutdown
      # SIGQUIT (3)  - Immediate shutdown
      # SIGTERM (15) - Smart shutdown
      crash.signals: '1 2 3 15'
      crash.delay: '60'
```

---

## Licenses and Copyright

`pg_crash`:

- **Copyright:** (c) 2017, 2025 CYBERTEC PostgreSQL International GmbH
- **License:** BSD 3-Clause License

All relevant license and copyright information for the `pg-crash` extension
and its dependencies are bundled within the image at:

```text
/licenses/
```

By using this image, you agree to comply with the terms of the licenses
contained therein.
