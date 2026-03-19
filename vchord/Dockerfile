ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        "postgresql-server-dev-${PG_MAJOR}"; \
    codename="$(. /etc/os-release && echo "${VERSION_CODENAME}")"; \
    if [ "${codename}" = "bookworm" ]; then \
        install -d -m 0755 /etc/apt/keyrings; \
        curl -fsSL https://apt.llvm.org/llvm-snapshot.gpg.key \
          | gpg --dearmor -o /etc/apt/keyrings/llvm.gpg; \
        echo "deb [signed-by=/etc/apt/keyrings/llvm.gpg] http://apt.llvm.org/${codename}/ llvm-toolchain-${codename}-18 main" \
          > /etc/apt/sources.list.d/llvm.list; \
        apt-get update; \
    fi; \
    apt-get install -y --no-install-recommends clang-18 libclang-18-dev; \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable; \
    . "$HOME/.cargo/env"; \
    rustup update stable; \
    ext_tag="${EXT_VERSION%%-*}"; \
    curl -fsSL "https://github.com/tensorchord/VectorChord/archive/refs/tags/${ext_tag}.tar.gz" \
      | tar -xz -C /tmp; \
    cd "/tmp/VectorChord-${ext_tag}"; \
    export CC=clang-18 CXX=clang++-18; \
    make build; \
    make install DESTDIR=/tmp/vchord-root; \
    install -Dm644 LICENSE "/tmp/vchord-root/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /tmp/vchord-root/usr/share/doc/postgresql-${PG_MAJOR}-vchord/copyright /licenses/postgresql-${PG_MAJOR}-vchord/

# Libraries
COPY --from=builder /tmp/vchord-root/usr/lib/postgresql/${PG_MAJOR}/lib/vchord* /lib/

# Share
COPY --from=builder /tmp/vchord-root/usr/share/postgresql/${PG_MAJOR}/extension/vchord* /share/extension/

USER 65532:65532
