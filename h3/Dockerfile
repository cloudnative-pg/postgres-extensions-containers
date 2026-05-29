# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

# Install extension via `apt-get`
RUN apt-get update && apt-get install -y --no-install-recommends \
      "postgresql-${PG_MAJOR}-h3=${EXT_VERSION}"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-h3/copyright /licenses/postgresql-${PG_MAJOR}-h3/
COPY --from=builder /usr/share/doc/libh3-1/copyright /licenses/libh3-1/

# Libraries (core h3 extension only; h3_postgis is intentionally excluded)
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/h3.so /lib/

# Share (core h3 extension only)
COPY --from=builder \
	/usr/share/postgresql/${PG_MAJOR}/extension/h3.control \
	/usr/share/postgresql/${PG_MAJOR}/extension/h3--*.sql \
	/share/extension/

# System libs: h3.so dynamically links libh3.so.1, which is not part of the
# base image. It is loaded at runtime via `ld_library_path = ["system"]`.
COPY --from=builder /usr/lib/*-linux-gnu/libh3.so.1 /system/

USER 65532:65532
