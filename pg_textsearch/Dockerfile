# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0


ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG TARGETARCH

USER 0

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends ca-certificates wget unzip dpkg; \
	case "${TARGETARCH}" in amd64|arm64) ;; *) echo "Unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; esac; \
	ZIP_URL="https://github.com/timescale/pg_textsearch/releases/download/v${EXT_VERSION}/pg-textsearch-v${EXT_VERSION}-pg${PG_MAJOR}-${TARGETARCH}.zip"; \
	DEB_FILE="pg-textsearch-postgresql-${PG_MAJOR}_${EXT_VERSION}-1_${TARGETARCH}.deb"; \
	LICENSE_TGZ_URL="https://github.com/timescale/pg_textsearch/releases/download/v${EXT_VERSION}/pg_textsearch-${EXT_VERSION}.tar.gz"; \
	mkdir -p /tmp/pg_textsearch && cd /tmp/pg_textsearch; \
	wget -O pg_textsearch.zip "$ZIP_URL"; \
	unzip -q pg_textsearch.zip "$DEB_FILE"; \
	dpkg-deb -x "./$DEB_FILE" /tmp/pkgroot; \
	mkdir -p /out/lib /out/share/extension "/out/licenses/pg-textsearch-postgresql-${PG_MAJOR}"; \
	cp -a "/tmp/pkgroot/usr/lib/postgresql/${PG_MAJOR}/lib/pg_textsearch"* /out/lib/; \
	cp -a "/tmp/pkgroot/usr/share/postgresql/${PG_MAJOR}/extension/pg_textsearch"* /out/share/extension/; \
	wget -qO- "$LICENSE_TGZ_URL" | tar -xzO "pg_textsearch-${EXT_VERSION}/LICENSE" > "/out/licenses/pg-textsearch-postgresql-${PG_MAJOR}/copyright"; \
	cd /; \
	rm -rf /tmp/pg_textsearch; \
	rm -rf /var/lib/apt/lists/*

FROM scratch
ARG PG_MAJOR

COPY --from=builder /out/licenses/pg-textsearch-postgresql-${PG_MAJOR}/copyright /licenses/pg-textsearch-postgresql-${PG_MAJOR}/
COPY --from=builder /out/lib/pg_textsearch* /lib/
COPY --from=builder /out/share/extension/pg_textsearch* /share/extension/

USER 65532:65532
