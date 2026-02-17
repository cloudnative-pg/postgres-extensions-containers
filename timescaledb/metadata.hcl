# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "timescaledb"
  sql_name                 = "timescaledb"
  image_name               = "timescaledb"
  shared_preload_libraries = ["timescaledb"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true
  versions = {
    trixie = {
        // renovate: datasource=postgresql depName=timescaledb-2-oss-postgresql-18 versioning=deb
        "18" = "2.24.0~debian13-1801"
    }
    bookworm = {
        // renovate: datasource=postgresql depName=timescaledb-2-oss-postgresql-18 versioning=deb
        "18" = "2.24.0~debian12-1801"
    }
  }
}
