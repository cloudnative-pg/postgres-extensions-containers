# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0


ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

# TODO: Remove this comment block after customizing the Dockerfile
# Instructions:
# 1. Remove all TODO comment blocks after completing the customization.
# 2. Uncomment and customize the COPY/RUN commands below.
# 3. If your extension requires additional system libraries, ensure they are
#    copied to /lib.

# Install extension via `apt-get`
RUN apt-get update && apt-get install -y --no-install-recommends \
      "postgresql-${PG_MAJOR}-repack=${EXT_VERSION}"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-repack/copyright  /licenses/postgresql-${PG_MAJOR}-repack/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_repack* /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_repack* /share/extension/

USER 65532:65532
