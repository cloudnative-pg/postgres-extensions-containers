# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pgrepack"
  sql_name                 = "pg_repack"
  image_name               = "pgrepack"
  licenses                 = ["BSD-3-Clause"]
  shared_preload_libraries = ["pg_repack"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  # TODO: Add these missing variables in the template
  env                   = {}
  postgresql_parameters = {}

  versions = {
    trixie = {
        "18" = {
          // renovate: suite=trixie-pgdg depName=postgresql-18-pg_repack
          package = "1.5.3-1.pgdg13+1"
          // Examples: \d+\.\d+ for major.minor (e.g., "18.0"), \d+\.\d+\.\d+ for major.minor.patch (e.g., "0.8.2")
          // renovate: suite=trixie-pgdg depName=postgresql-18-pg_repack extractVersion=^(?<version>\d+\.\d+\.\d+)
          sql = "1.5.3"
        }
    }
    bookworm = {
        "18" = {
          // renovate: suite=bookworm-pgdg depName=postgresql-18-pg_repack
          package = "1.5.3-1.pgdg12+1"
          // Examples: \d+\.\d+ for major.minor (e.g., "18.0"), \d+\.\d+\.\d+ for major.minor.patch (e.g., "0.8.2")
          // renovate: suite=bookworm-pgdg depName=postgresql-18-pg_repack extractVersion=^(?<version>\d+\.\d+\.\d+)
          sql = "1.5.3"
        }
    }
  }
}
