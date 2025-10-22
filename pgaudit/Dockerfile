ARG PG_VERSION=18
ARG DISTRO=bookworm
FROM ghcr.io/cloudnative-pg/postgresql:${PG_VERSION}-minimal-${DISTRO} AS builder

ARG PG_VERSION
ARG DISTRO

USER 0

COPY . /tmp/pgaudit

RUN set -eux; \
	mkdir -p /opt/extension && \
	apt-get update && \
	apt-get install -y --no-install-recommends build-essential git "postgresql-server-dev-${PG_VERSION}=${PG_VERSION}*" libkrb5-dev libxml2-dev && \
	cd /tmp/pgaudit && \
	git checkout REL_18_STABLE && \
	PG_CONFIG=/usr/lib/postgresql/${PG_VERSION}/bin/pg_config USE_PGXS=1 make clean && \
	PG_CONFIG=/usr/lib/postgresql/${PG_VERSION}/bin/pg_config USE_PGXS=1 OPTFLAGS="" make && \
	PG_CONFIG=/usr/lib/postgresql/${PG_VERSION}/bin/pg_config USE_PGXS=1 make install datadir=/opt/extension/share/ pkglibdir=/opt/extension/lib/

FROM scratch

COPY --from=builder /opt/extension/lib/ /lib/
COPY --from=builder /opt/extension/share/ /share/