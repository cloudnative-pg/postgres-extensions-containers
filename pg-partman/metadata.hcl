# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-partman"
  sql_name                 = "pg_partman"
  image_name               = "pg-partman"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_partman_bgw"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = ["bin"]
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-partman
      "18" = "5.4.3-1.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-partman
      "18" = "5.4.3-1.pgdg13+1"
    }
  }
}
