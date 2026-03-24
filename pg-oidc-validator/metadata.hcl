# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-oidc-validator"
  sql_name                 = "pg_oidc_validator"
  image_name               = "pg-oidc-validator"
  licenses                 = ["Apache-2.0"]
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = false

  versions = {
    bookworm = {
      "18" = "0.2"
    }
    trixie = {
      "18" = "0.2"
    }
  }
}

target "default" {
  name = "${metadata.name}-${sanitize(getExtensionVersion(distro, pgVersion))}-${pgVersion}-${distro}"
  matrix = {
    pgVersion = pgVersions
    distro    = distributions
  }

  platforms = [
    "linux/amd64"
  ]
}
