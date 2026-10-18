# syntax=docker/dockerfile:1.28

# Python 3.14 is the newest version supported by the pinned ScanCode 32.5.0.
# Move to a newer Python as soon as ScanCode supports it; keep this aligned with SCANCODE_VERSION below.
# https://github.com/aboutcode-org/scancode-toolkit/releases/tag/v32.5.0
# renovate: datasource=docker depName=python packageName=library/python versioning=docker
FROM python:3.14-slim-bookworm@sha256:48b13b003dda20b16f9442b8475aa05fe21bf6579a8c881db92ffb4d8fd20f83

ARG TARGETARCH
# renovate: datasource=github-releases depName=anchore/syft versioning=semver
ARG SYFT_VERSION=1.54.1

# renovate: datasource=pypi depName=scancode-toolkit versioning=pep440
ARG SCANCODE_VERSION=32.5.0
COPY dependencies/ /tmp/dependencies/

# ScanCode's bundled native libraries are not available on every architecture.
# Use Debian's libraries and an explicit path for ExtractCode's libarchive lookup.
ENV EXTRACTCODE_LIBARCHIVE_PATH=/usr/local/lib/libarchive.so.13 \
    TYPECODE_LIBMAGIC_DB_PATH=/usr/share/misc/magic.mgc

RUN apt-get update \
    && xargs apt-get install --no-install-recommends -y < "/tmp/dependencies/debian-${TARGETARCH}.txt" \
    && ln -s /usr/lib/*-linux-gnu/libarchive.so.13 /usr/local/lib/libarchive.so.13 \
    && rm -rf /var/lib/apt/lists/* \
    && curl --fail --silent --show-error --location \
      "https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}/syft_${SYFT_VERSION}_linux_${TARGETARCH}.tar.gz" \
      | tar -xz -C /usr/local/bin syft \
    && curl --fail --silent --show-error --location \
      "https://raw.githubusercontent.com/aboutcode-org/scancode-toolkit/v${SCANCODE_VERSION}/requirements.txt" \
      --output /tmp/scancode-constraints.txt \
    && test -s /tmp/scancode-constraints.txt \
    && if [ "$TARGETARCH" = arm64 ]; then \
      sed -i '/^extractcode-7z==/d; /^extractcode-libarchive==/d; /^typecode-libmagic==/d' /tmp/scancode-constraints.txt; \
    fi \
    && python -m pip install --no-cache-dir \
      "scancode-toolkit==${SCANCODE_VERSION}" -c /tmp/scancode-constraints.txt \
    && python -m pip check \
    && syft version \
    && scancode --version

WORKDIR /opt/cnpg-sbom-generator
COPY compose.py generator.py hooks.py spdx_validation.py ./

ARG SBOM_GENERATOR_REVISION=unknown
ENV SBOM_GENERATOR_REVISION=${SBOM_GENERATOR_REVISION}
LABEL org.opencontainers.image.revision=${SBOM_GENERATOR_REVISION}

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "/opt/cnpg-sbom-generator/generator.py"]
