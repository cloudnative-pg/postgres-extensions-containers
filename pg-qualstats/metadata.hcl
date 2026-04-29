# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-qualstats"
  sql_name                 = "pg_qualstats"
  image_name               = "pg-qualstats"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pg_qualstats"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-qualstats
      "18" = "2.1.3-1.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-pg-qualstats
      "18" = "2.1.3-1.pgdg13+1"
    }
  }
}
