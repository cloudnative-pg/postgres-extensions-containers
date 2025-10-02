ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG DISTRO=trixie

USER 0

RUN set -eux; \
    apt-get update; \
	apt-get install -y --no-install-recommends "postgresql-${PG_MAJOR}-pgaudit=${EXT_VERSION}"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-pgaudit/copyright /licenses/postgresql-${PG_MAJOR}-pgaudit/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pgaudit* /lib/
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/ /lib/bitcode/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pgaudit* /share/extension/

USER 65532:65532