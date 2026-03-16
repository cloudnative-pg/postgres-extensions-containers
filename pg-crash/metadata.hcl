# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-crash"
  sql_name                 = "pg_crash"
  image_name               = "pg-crash"
  licenses                 = ["BSD-3-Clause"]
  shared_preload_libraries = ["pg_crash"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = false

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-crash
      "18" = "0.3-2.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-pg-crash
      "18" = "0.3-2.pgdg13+1"
    }
  }
}
