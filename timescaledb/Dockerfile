
ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends gnupg postgresql-common apt-transport-https lsb-release wget ca-certificates; \
    # Add TimescaleDB package repository
    echo "deb https://packagecloud.io/timescale/timescaledb/debian/ $(lsb_release -c -s) main" > /etc/apt/sources.list.d/timescaledb.list; \
    wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        timescaledb-2-oss-postgresql-${PG_MAJOR}=${EXT_VERSION}*

######################################################################
# Final SCRATCH image
######################################################################
FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/timescaledb-2-oss-postgresql-${PG_MAJOR}/copyright /licenses/timescaledb/

# Libraries — .so and bitcode for TimescaleDB
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/timescaledb* /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/timescaledb-2* /lib/
 
# Extension SQL + control files
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/timescaledb* /share/extension/

USER 65532:65532