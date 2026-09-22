ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION
ARG POSTGIS_MAJOR

USER 0

COPY scripts/stage_system_libs.sh /usr/local/bin/stage_system_libs.sh

RUN set -eux && \
	# Initial system libraries
	ldconfig -p | awk '{print $NF}' | grep '^/' | sort | uniq > /tmp/base-image-libs.out && \
	# Install PostGIS
	apt-get update && \
	apt-get install -y --no-install-recommends \
		"postgresql-${PG_MAJOR}-postgis-${POSTGIS_MAJOR}=${EXT_VERSION}" \
		"postgresql-${PG_MAJOR}-postgis-${POSTGIS_MAJOR}-scripts=${EXT_VERSION}"

# Strip the "$libdir/" prefix from LOAD and CREATE FUNCTION ... AS statements
# in the extension and contrib scripts: with imageVolume-mounted extensions
# there is no $libdir to expand, and PostgreSQL 18+ fails to resolve it during
# CREATE/ALTER EXTENSION otherwise.
# dynamic_library_path already resolves the bare module name.
# Only strip right after an opening quote, so the pattern can't accidentally
# touch unrelated text.
RUN sed -i "s/'\$libdir\//'/g" \
	/usr/share/postgresql/${PG_MAJOR}/extension/postgis*.sql \
	/usr/share/postgresql/${PG_MAJOR}/extension/address_standardizer*.sql \
	/usr/share/postgresql/${PG_MAJOR}/contrib/postgis*/*.sql

# Gather PostGIS system libraries and their licenses
RUN /usr/local/bin/stage_system_libs.sh \
	/usr/lib/postgresql/${PG_MAJOR}/lib/address_standardizer*.so \
	/usr/lib/postgresql/${PG_MAJOR}/lib/postgis*.so


FROM scratch
ARG PG_MAJOR
ARG POSTGIS_MAJOR

# Licenses
COPY --from=builder /licenses /licenses/
COPY --from=builder /usr/share/doc/postgresql-${PG_MAJOR}-postgis-${POSTGIS_MAJOR}/copyright /licenses/postgresql-${PG_MAJOR}-postgis-${POSTGIS_MAJOR}/

# Libraries
COPY --from=builder \
	/usr/lib/postgresql/${PG_MAJOR}/lib/address_standardizer* \
	/usr/lib/postgresql/${PG_MAJOR}/lib/postgis* \
	/lib/

COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/bitcode/ /lib/bitcode/

# Share
COPY --from=builder \
	/usr/share/postgresql/${PG_MAJOR}/extension/address_standardizer* \
	/usr/share/postgresql/${PG_MAJOR}/extension/postgis* \
	/share/extension/

COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/contrib/postgis* /share/contrib/
COPY --from=builder /usr/share/gdal/ /share/gdal/
COPY --from=builder /usr/share/proj/ /share/proj/

# System libs
COPY --from=builder /system /system/

USER 65532:65532
