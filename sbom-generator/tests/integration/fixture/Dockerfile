# syntax=docker/dockerfile:1.7
ARG BUILDKIT_SBOM_SCAN_STAGE=builder

FROM debian:bookworm-slim AS builder

COPY augment_spdx.py /usr/local/share/cnpg-sbom/augment_spdx.py

RUN mkdir -p /fixture/licenses/libc6 /fixture/licenses/zlib1g \
    && cp /usr/share/doc/base-files/copyright /fixture/licenses/copyright \
    && cp /usr/share/doc/libc6/copyright /fixture/licenses/libc6/copyright \
    && cp /usr/share/doc/zlib1g/copyright /fixture/licenses/zlib1g/copyright

FROM scratch
COPY --from=builder /fixture/licenses /licenses
