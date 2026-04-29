# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0

ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN set -eux && \
	# Initial system libraries
	ldconfig -p | awk '{print $NF}' | grep '^/' | sort | uniq > /tmp/base-image-libs.out && \
	# Install runtime dependency (libcurl) and download tool
	apt-get update && \
	apt-get install -y --no-install-recommends wget libcurl4 && \
	# Download and install extension from GitHub releases ("latest" tag)
	wget -q -O /tmp/pg-oidc-validator.deb \
		"https://github.com/Percona-Lab/pg_oidc_validator/releases/download/latest/pg-oidc-validator-pgdg${PG_MAJOR}.deb" && \
	dpkg -i /tmp/pg-oidc-validator.deb && \
	rm /tmp/pg-oidc-validator.deb

# Gather system libraries not already in the base image
RUN mkdir -p /system /licenses && \
	ldd /usr/lib/postgresql/${PG_MAJOR}/lib/pg_oidc_validator.so \
		| awk '{print $3}' | grep '^/' | sort | uniq > /tmp/all-deps.out && \
	comm -13 /tmp/base-image-libs.out /tmp/all-deps.out > /tmp/libraries.out && \
	while read -r lib; do \
		resolved=$(readlink -f "$lib"); \
		dir=$(dirname "$lib"); \
		base=$(basename "$lib"); \
		cp -a "$resolved" /system/; \
		for file in "$dir"/"${base%.so*}.so"*; do \
			[ -e "$file" ] || continue; \
			if [ -L "$file" ] && [ "$(readlink -f "$file")" = "$resolved" ]; then \
				ln -sf "$(basename "$resolved")" "/system/$(basename "$file")"; \
			fi; \
		done; \
	done < /tmp/libraries.out && \
	# Get licenses for each system library
	for lib in $(find /system -maxdepth 1 -type f -name '*.so*'); do \
		pkg=$(dpkg -S "$(basename "$lib")" | grep -v "diversion by" | awk -F: '/:/{print $1; exit}'); \
		[ -z "$pkg" ] && continue; \
		mkdir -p "/licenses/$pkg" && cp -a "/usr/share/doc/$pkg/copyright" "/licenses/$pkg/copyright"; \
	done

FROM scratch
ARG PG_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/pg_oidc_validator.so /lib/

# System libs (libcurl and transitive dependencies)
COPY --from=builder /system /system/

USER 65532:65532
