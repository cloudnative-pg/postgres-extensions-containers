variable "environment" {
  default = "testing"
  validation {
    condition = contains(["testing", "production"], environment)
    error_message = "environment must be either testing or production"
  }
}

variable "registry" {
  default = "localhost:5000"
}

// Use the revision variable to identify the commit that generated the image
variable "revision" {
  default = ""
}

variable "distributions" {
  default = [
    "bookworm",
    "trixie"
  ]
}

variable "pgVersions" {
  default = [
    "18"
  ]
}

fullname = ( environment == "testing") ? "${registry}/${metadata.image_name}-testing" : "${registry}/${metadata.image_name}"
now = timestamp()
authors = "The CloudNativePG Contributors"
url = "https://github.com/cloudnative-pg/postgres-extensions-containers"

target "default" {
  matrix = {
    pgVersion = pgVersions
    distro = distributions
  }

  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]

  dockerfile = "Dockerfile"
  context = "${metadata.name}/"
  name = "${metadata.name}-${sanitize(getExtensionVersion(distro, pgVersion))}-${pgVersion}-${distro}"

  tags = [
    "${getImageName(fullname)}:${getExtensionVersion(distro, pgVersion)}-${pgVersion}-${distro}",
    "${getImageName(fullname)}:${getExtensionVersion(distro, pgVersion)}-${formatdate("YYYYMMDDhhmm", now)}-${pgVersion}-${distro}",
  ]

  args = {
    PG_MAJOR = "${pgVersion}"
    EXT_VERSION = "${getExtensionPackage(distro, pgVersion)}"
    BASE = "${getBaseImage(distro, pgVersion)}"
  }

  attest = [
    "type=provenance,mode=max",
    "type=sbom"
  ]
  annotations = [
    "index,manifest:org.opencontainers.image.created=${now}",
    "index,manifest:org.opencontainers.image.url=${url}",
    "index,manifest:org.opencontainers.image.source=${url}",
    "index,manifest:org.opencontainers.image.version=${getExtensionVersion(distro, pgVersion)}",
    "index,manifest:org.opencontainers.image.revision=${revision}",
    "index,manifest:org.opencontainers.image.vendor=${authors}",
    "index,manifest:org.opencontainers.image.title=${metadata.name} ${getExtensionVersion(distro, pgVersion)} ${pgVersion} ${distro}",
    "index,manifest:org.opencontainers.image.description=A ${metadata.name} ${getExtensionVersion(distro, pgVersion)} container image for PostgreSQL ${pgVersion} on ${distro}",
    "index,manifest:org.opencontainers.image.documentation=${url}",
    "index,manifest:org.opencontainers.image.authors=${authors}",
    "index,manifest:org.opencontainers.image.licenses=Apache-2.0",
    "index,manifest:org.opencontainers.image.base.name=scratch",
    "index,manifest:io.cloudnativepg.image.base.name=${getBaseImage(distro, pgVersion)}",
    "index,manifest:io.cloudnativepg.image.base.pgmajor=${pgVersion}",
    "index,manifest:io.cloudnativepg.image.base.os=${distro}",
  ]
  labels = {
    "org.opencontainers.image.created" = "${now}",
    "org.opencontainers.image.url" = "${url}",
    "org.opencontainers.image.source" = "${url}",
    "org.opencontainers.image.version" = "${getExtensionVersion(distro, pgVersion)}",
    "org.opencontainers.image.revision" = "${revision}",
    "org.opencontainers.image.vendor" = "${authors}",
    "org.opencontainers.image.title" = "${metadata.name} ${getExtensionVersion(distro, pgVersion)} ${pgVersion} ${distro}",
    "org.opencontainers.image.description" = "A ${metadata.name} ${getExtensionVersion(distro, pgVersion)} container image for PostgreSQL ${pgVersion} on ${distro}",
    "org.opencontainers.image.documentation" = "${url}",
    "org.opencontainers.image.authors" = "${authors}",
    "org.opencontainers.image.licenses" = "Apache-2.0",
    "org.opencontainers.image.base.name" = "scratch",
    "io.cloudnativepg.image.base.name" = "${getBaseImage(distro, pgVersion)}",
    "io.cloudnativepg.image.base.pgmajor" = "${pgVersion}",
    "io.cloudnativepg.image.base.os" = "${distro}",
  }
}

function getImageName {
  params = [ name ]
  result = lower(name)
}

function getExtensionPackage {
  params = [ distro, pgVersion ]
  result = metadata.versions[distro][pgVersion]
}

// Parse the packageVersion to extract the MM.mm.pp extension version.
// We capture the first digit, and then zero or more sequences of ".digits". (e.g 0.8.1-2.pgdg13+1 -> 0.8.1)
// If the package starts with an epoch, we use it and replace the ":" with a "-" (e.g 1:6.1.0-2.pgdg130+1 -> 1-6.1.0)
function getExtensionVersion {
  params = [ distro, pgVersion ]
  result = replace(
    regex("^(?:[0-9]+:)?[0-9]+(?:\\.[0-9]+)*", getExtensionPackage(distro, pgVersion)),
    ":", "-")
}

function getBaseImage {
  params = [ distro, pgVersion ]
  result = format("ghcr.io/cloudnative-pg/postgresql:%s-minimal-%s", pgVersion, distro)
}
