# Build stage - extract extension files from .deb package
FROM ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie AS builder

ARG PG_MAJOR=18
ARG EXT_VERSION=2.0.0

USER 0

RUN set -eux; \
	ARCH=$(dpkg --print-architecture); \
	mkdir -p /extension-build && \
	apt-get update && \
	apt-get install -y --no-install-recommends wget ca-certificates && \
	cd /tmp && \
	DOWNLOAD_URL="https://github.com/pmpetit/pglinter/releases/download/${EXT_VERSION}/postgresql_pglinter_${PG_MAJOR}_${EXT_VERSION}_${ARCH}.deb" && \
	echo "Downloading pglinter from: $DOWNLOAD_URL" && \
	wget -O pglinter.deb "$DOWNLOAD_URL" && \
	dpkg-deb -x pglinter.deb /tmp/extracted && \
	echo "Contents of extracted package:" && \
	find /tmp/extracted -type f && \
	# Create CloudNative-PG compliant directory structure
	mkdir -p /extension-build/lib /extension-build/share/extension && \
	# Copy shared libraries (.so files)
	if [ -d /tmp/extracted/usr/lib/postgresql/${PG_MAJOR}/lib ]; then \
		echo "Copying libraries from /usr/lib/postgresql/${PG_MAJOR}/lib/"; \
		find /tmp/extracted/usr/lib/postgresql/${PG_MAJOR}/lib/ -name "*.so" -exec cp {} /extension-build/lib/ \; ; \
	fi && \
	# Copy extension control and SQL files
	if [ -d /tmp/extracted/usr/share/postgresql/${PG_MAJOR}/extension ]; then \
		echo "Copying extension files from /usr/share/postgresql/${PG_MAJOR}/extension/"; \
		cp /tmp/extracted/usr/share/postgresql/${PG_MAJOR}/extension/* /extension-build/share/extension/ ; \
	fi && \
	echo "Final extension structure:" && \
	find /extension-build -type f

FROM scratch
ARG PG_MAJOR=18

# Final image - scratch base following CloudNative-PG specifications
# Licenses
COPY copyright /licenses/postgresql-${PG_MAJOR}-pglinter/

COPY --from=builder /extension-build/lib/ /lib/
COPY --from=builder /extension-build/share/ /share/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pglinter* /share/extension/

USER 65532:65532