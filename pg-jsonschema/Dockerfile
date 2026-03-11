ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG PGRX_VERSION=0.16.1

USER 0

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential \
        libpq-dev \
        "postgresql-server-dev-${PG_MAJOR}" \
        pkg-config \
        cmake \
        clang \
        libclang-dev; \
    rm -rf /var/lib/apt/lists/*

ENV PATH=/root/.cargo/bin:${PATH}

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --profile minimal --default-toolchain stable
RUN cargo install cargo-pgrx --version "${PGRX_VERSION}" --locked
RUN cargo pgrx init --pg"${PG_MAJOR}"=/usr/lib/postgresql/"${PG_MAJOR}"/bin/pg_config

WORKDIR /tmp
RUN set -eux; \
    curl -fsSL -o pg_jsonschema.tar.gz "https://github.com/supabase/pg_jsonschema/archive/refs/tags/v${EXT_VERSION}.tar.gz"; \
    tar -xzf pg_jsonschema.tar.gz; \
    mv "pg_jsonschema-${EXT_VERSION}" pg_jsonschema

WORKDIR /tmp/pg_jsonschema
RUN set -eux; \
    cargo pgrx install --release --no-default-features --features "pg${PG_MAJOR}" --pg-config /usr/lib/postgresql/"${PG_MAJOR}"/bin/pg_config

RUN install -D -m 0644 /tmp/pg_jsonschema/LICENSE /licenses/pg_jsonschema/LICENSE

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_jsonschema.so /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_jsonschema* /share/extension/

USER 65532:65532
