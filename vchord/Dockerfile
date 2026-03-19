ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG TARGETARCH

USER 0

RUN set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dpkg; \
    ext_tag="${EXT_VERSION%%-*}"; \
    package_name="postgresql-${PG_MAJOR}-vchord_${ext_tag}-1_${TARGETARCH}.deb"; \
    curl -fsSL -o /tmp/vchord.deb \
      "https://github.com/tensorchord/VectorChord/releases/download/${ext_tag}/${package_name}"; \
    dpkg-deb -x /tmp/vchord.deb /tmp/vchord-root; \
    install -Dm644 /dev/null "/tmp/vchord-root/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright"; \
    curl -fsSL "https://raw.githubusercontent.com/tensorchord/VectorChord/${ext_tag}/LICENSE" \
      -o "/tmp/vchord-root/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /tmp/vchord-root/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright /licenses/postgresql-${PG_MAJOR}-vchord/

# Libraries
COPY --from=builder /tmp/vchord-root/usr/lib/postgresql/${PG_MAJOR}/lib/vchord* /lib/

# Share
COPY --from=builder /tmp/vchord-root/usr/share/postgresql/${PG_MAJOR}/extension/vchord* /share/extension/

USER 65532:65532
