ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN set -eux; \
    ext_tag="${EXT_VERSION%%-*}"; \
    arch="$(dpkg --print-architecture)"; \
    package_name="postgresql-${PG_MAJOR}-vchord_${ext_tag}-1_${arch}.deb"; \
    apt-get update && \
    apt-get install -y --no-install-recommends wget ca-certificates && \
    wget "https://github.com/tensorchord/VectorChord/releases/download/${ext_tag}/${package_name}" -P /tmp && \
    dpkg-deb -x "/tmp/${package_name}" /sysroot && \
    install -Dm644 /dev/null "/sysroot/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright" && \
    wget "https://raw.githubusercontent.com/tensorchord/VectorChord/${ext_tag}/LICENSE" \
      -O "/sysroot/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright" && \
    apt-get remove -y wget ca-certificates && \
    apt-get purge -y --auto-remove && \
    rm -rf /tmp/* /var/lib/apt/lists/*

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /sysroot/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright /licenses/postgresql-${PG_MAJOR}-vchord/

# Libraries
COPY --from=builder /sysroot/usr/lib/postgresql/${PG_MAJOR}/lib/vchord* /lib/

# Share
COPY --from=builder /sysroot/usr/share/postgresql/${PG_MAJOR}/extension/vchord* /share/extension/

USER 65532:65532
