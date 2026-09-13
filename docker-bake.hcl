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

fullname = ( environment == "testing") ? "${registry}/${metadata.image_name}-testing" : "${registry}/${metadata.image_name}"
now = timestamp()
authors = "The CloudNativePG Contributors"
url = "https://github.com/cloudnative-pg/postgres-extensions-containers"

target "default" {
  matrix = {
    build = getBuildMatrix()
  }

  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]

  dockerfile = "Dockerfile"
  context = "${metadata.name}/"
  name = getBuildName(metadata.name, build.distro, build.pgVersion)

  tags = [
    "${getImageName(fullname)}:${getExtensionVersion(build.distro, build.pgVersion)}-${build.pgVersion}-${build.distro}",
    "${getImageName(fullname)}:${getExtensionVersion(build.distro, build.pgVersion)}-${formatdate("YYYYMMDDhhmm", now)}-${build.pgVersion}-${build.distro}",
  ]

  args = {
    PG_MAJOR = "${build.pgVersion}"
    EXT_VERSION = "${getExtensionPackage(build.distro, build.pgVersion)}"
    BASE = "${getBaseImage(build.distro, build.pgVersion)}"
  }

  output = [
    "type=image,oci-mediatypes=true,oci-artifact=true",
  ]
  attest = [
    "type=provenance,mode=max",
    "type=sbom"
  ]
  annotations = [
    "index,manifest:org.opencontainers.image.created=${now}",
    "index,manifest:org.opencontainers.image.url=${url}",
    "index,manifest:org.opencontainers.image.source=${url}",
    "index,manifest:org.opencontainers.image.version=${getExtensionVersion(build.distro, build.pgVersion)}",
    "index,manifest:org.opencontainers.image.revision=${revision}",
    "index,manifest:org.opencontainers.image.vendor=${authors}",
    "index,manifest:org.opencontainers.image.title=${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} ${build.pgVersion} ${build.distro}",
    "index,manifest:org.opencontainers.image.description=A ${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} container image for PostgreSQL ${build.pgVersion} on ${build.distro}",
    "index,manifest:org.opencontainers.image.documentation=${url}",
    "index,manifest:org.opencontainers.image.authors=${authors}",
    "index,manifest:org.opencontainers.image.licenses=${join(" AND ", metadata.licenses)}",
    "index,manifest:org.opencontainers.image.base.name=scratch",
    "index,manifest:io.cloudnativepg.image.base.name=${getBaseImage(build.distro, build.pgVersion)}",
    "index,manifest:io.cloudnativepg.image.base.pgmajor=${build.pgVersion}",
    "index,manifest:io.cloudnativepg.image.base.os=${build.distro}",
    "index,manifest:io.cloudnativepg.image.sql.version=${getExtensionSqlVersion(build.distro, build.pgVersion)}",
  ]
  labels = {
    "org.opencontainers.image.created" = "${now}",
    "org.opencontainers.image.url" = "${url}",
    "org.opencontainers.image.source" = "${url}",
    "org.opencontainers.image.version" = "${getExtensionVersion(build.distro, build.pgVersion)}",
    "org.opencontainers.image.revision" = "${revision}",
    "org.opencontainers.image.vendor" = "${authors}",
    "org.opencontainers.image.title" = "${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} ${build.pgVersion} ${build.distro}",
    "org.opencontainers.image.description" = "A ${metadata.name} ${getExtensionVersion(build.distro, build.pgVersion)} container image for PostgreSQL ${build.pgVersion} on ${build.distro}",
    "org.opencontainers.image.documentation" = "${url}",
    "org.opencontainers.image.authors" = "${authors}",
    "org.opencontainers.image.licenses" = "${join(" AND ", metadata.licenses)}",
    "org.opencontainers.image.base.name" = "scratch",
    "io.cloudnativepg.image.base.name" = "${getBaseImage(build.distro, build.pgVersion)}",
    "io.cloudnativepg.image.base.pgmajor" = "${build.pgVersion}",
    "io.cloudnativepg.image.base.os" = "${build.distro}",
    "io.cloudnativepg.image.sql.version" = "${getExtensionSqlVersion(build.distro, build.pgVersion)}",
  }
}

function getImageName {
  params = [ name ]
  result = lower(name)
}

function getBuildName {
  params = [ extName, distro, pgVersion ]
  result = format("%s-%s-%s-%s", extName, sanitize(getExtensionVersion(distro, pgVersion)), pgVersion, distro)
}

// The build matrix is the explicit set of (distro, pgVersion) pairs declared
// in metadata.versions. Using a single flattened dimension (instead of a
// cross-product of two lists) lets each distribution declare its own set of
// PG majors without producing combinations that don't exist.
function getBuildMatrix {
  params = []
  result = flatten([
    for distro in keys(metadata.versions) : [
      for pgVersion in keys(metadata.versions[distro]) : {
        distro    = distro
        pgVersion = pgVersion
      }
    ]
  ])
}

function getExtensionPackage {
  params = [ distro, pgVersion ]
  result = metadata.versions[distro][pgVersion]["package"]
}

function getExtensionSqlVersion {
  params = [ distro, pgVersion ]
  result = lookup(metadata.versions[distro][pgVersion], "sql", "")
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
