# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg_ivm"
  sql_name                 = "pg_ivm"
  image_name               = "pg_ivm"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    trixie = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-ivm
        "18" = "1.13-1.pgdg13+1"
    }
    bookworm = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-ivm
        "18" = "1.13-1.pgdg12+1"
    }
  }
}
