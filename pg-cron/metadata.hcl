# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "pg-cron"
  image_name               = "pg-cron"

  licenses                 = ["PostgreSQL"]

  sql_name                 = "pg_cron"
  shared_preload_libraries = ["pg_cron"]
  # cron.database_name must match the database where CREATE EXTENSION is run
  postgresql_parameters    = { "cron.database_name" = "app" }
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-cron
        package = "1.6.7-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-cron extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.6"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-cron
        package = "1.6.7-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-cron extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.6"
      }
    }
  }
}
