# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "timescaledb-oss"
  sql_name                 = "timescaledb"
  image_name               = "timescaledb-oss"
  licenses                 = ["Apache-2.0"]
  shared_preload_libraries = ["timescaledb"]
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-timescaledb
        package = "2.26.1+dfsg-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-timescaledb extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql = "2.26.1"
      }
    }
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-timescaledb
        package = "2.26.1+dfsg-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-timescaledb extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql = "2.26.1"
      }
    }
  }
}
