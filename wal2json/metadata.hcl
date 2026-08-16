# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "wal2json"
  sql_name                 = "wal2json"
  image_name               = "wal2json"
  licenses                 = ["BSD-3-Clause"]
  shared_preload_libraries = []
  # PostgreSQL 18.6+ restricts logical decoding output plugins to an
  # allow-list (CVE-2026-6471). Without this, pg_create_logical_replication_slot(...,
  # 'wal2json') fails with "library wal2json may not be used as an output
  # plugin". pgoutput/test_decoding are the built-in defaults; they must be
  # re-listed here because setting this parameter replaces PostgreSQL's
  # default rather than extending it.
  postgresql_parameters    = { output_plugin_libraries = "pgoutput, test_decoding, wal2json" }
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
        package = "2.6-4.pgdg12+1"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-wal2json
        package = "2.6-4.pgdg13+1"
      }
    }
  }
}
