# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

# Install extension via `apt-get`
RUN apt-get update && apt-get install -y --no-install-recommends \
      "postgresql-${PG_MAJOR}-partman=${EXT_VERSION}"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-partman/copyright /licenses/postgresql-${PG_MAJOR}-partman/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_partman_bgw.so /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/ /lib/bitcode/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_partman* /share/extension/

# Binaries (maintenance scripts)
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/bin/check_unique_constraint.py /bin/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/bin/dump_partition.py /bin/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/bin/vacuum_maintenance.py /bin/

USER 65532:65532
