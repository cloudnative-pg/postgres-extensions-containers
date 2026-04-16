ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG TARGETARCH

USER 0

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl; \
    rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64) arch="amd64" ;; \
        arm64) arch="arm64" ;; \
        *) echo "unsupported architecture: ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/pg_jsonschema.deb \
        "https://github.com/supabase/pg_jsonschema/releases/download/v${EXT_VERSION}/pg_jsonschema-v${EXT_VERSION}-pg${PG_MAJOR}-${arch}-linux-gnu.deb"; \
    dpkg -i /tmp/pg_jsonschema.deb; \
    rm /tmp/pg_jsonschema.deb; \
    curl -fsSL -o /licenses/pg_jsonschema/LICENSE \
        --create-dirs \
        "https://raw.githubusercontent.com/supabase/pg_jsonschema/v${EXT_VERSION}/LICENSE"

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_jsonschema.so /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/pg_jsonschema* /share/extension/

USER 65532:65532
