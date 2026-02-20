# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "timescaledb-oss"
  sql_name                 = "timescaledb"
  image_name               = "timescaledb-oss"
  shared_preload_libraries = ["timescaledb"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true
  versions = {
    trixie = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-timescaledb
        "18" = "2.25.1+dfsg-1.pgdg13+1"
    }
    bookworm = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-timescaledb
        "18" = "2.25.1+dfsg-1.pgdg12+1"
    }
  }
}
