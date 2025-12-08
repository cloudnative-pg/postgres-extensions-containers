ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        postgresql-server-dev-${PG_MAJOR}; \
    # Clone and build pg_ivm from source
    git clone --branch "v${EXT_VERSION}" --depth 1 https://github.com/sraoss/pg_ivm.git /build/pg_ivm; \
    cd /build/pg_ivm; \
    make USE_PGXS=1; \
    make USE_PGXS=1 install

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /build/pg_ivm/LICENSE /licenses/pg_ivm/LICENSE

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_ivm* /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_ivm* /share/extension/

USER 65532:65532