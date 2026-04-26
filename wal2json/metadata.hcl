# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "wal2json"
  sql_name                 = "wal2json"
  image_name               = "wal2json"
  licenses                 = ["BSD-3-Clause"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = false

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-wal2json
        package = "2.6-3.pgdg12+1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-wal2json
        package = "2.6-3.pgdg13+1"
      }
    }
  }
}
