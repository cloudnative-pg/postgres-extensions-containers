ARG BASE=ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
FROM $BASE AS builder

ARG PG_MAJOR
ARG EXT_VERSION

USER 0

RUN apt-get update && \
    apt-get install -y curl lsb-release

#RUN CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
#RUN echo "deb https://repo.dalibo.com/apt/ $CODENAME main" > /etc/apt/sources.list.d/dalibo_labs.list
RUN curl -fsSL https://repo.dalibo.com/install.sh | sh
# RUN cat /etc/apt/sources.list.d/dalibo_labs.list
# RUN curl -fsSL -o /etc/apt/trusted.gpg.d/dalibo_labs.asc https://repo.dalibo.com/dalibo_labs.asc

RUN apt-get update && \
    apt-get install -y postgresql_anonymizer_${PG_MAJOR}=${EXT_VERSION}

FROM scratch
ARG PG_MAJOR

# Licenses
#COPY --from=builder /usr/share/doc/postgresql-18-pganon/copyright /licenses/postgresql-18-pganon/

# Libraries
COPY --from=builder /usr/lib/postgresql/${PG_MAJOR}/lib/anon* /lib/

# Share
COPY --from=builder /usr/share/postgresql/${PG_MAJOR}/extension/anon* /share/extension/

USER 65532:65532
