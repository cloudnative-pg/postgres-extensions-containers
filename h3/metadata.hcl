# SPDX-FileCopyrightText: Copyright © contributors to CloudNativePG, established as CloudNativePG a Series of LF Projects, LLC.
# SPDX-License-Identifier: Apache-2.0
metadata = {
  name                     = "h3"
  sql_name                 = "h3"
  image_name               = "h3"

  # h3-pg (the PostgreSQL bindings) and the bundled libh3 C library are both
  # released upstream under Apache-2.0.
  #
  # CAVEAT: the Debian `libh3-1` package ships a `copyright` file that
  # classifies two upstream files (`README.md` and `src/h3lib/lib/coordijk.c`)
  # as AGPL-3+, attributing them to DGGRID / Southern Oregon University. This
  # appears to be an over-conservative Debian classification of an
  # algorithm-origin credit: the current upstream (uber/h3) carries Apache-2.0
  # headers on those files and contains no AGPL license text. This is flagged
  # here for maintainer review, since `coordijk.c` is compiled into the bundled
  # `libh3.so.1`.
  licenses                 = ["Apache-2.0"]

  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []

  # `h3.so` dynamically links the non-base `libh3.so.1` system library, which
  # the Dockerfile bundles under `/system` (see the `postgis` extension for the
  # same pattern).
  ld_library_path          = ["system"]

  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-h3
        package = "4.2.3-4.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-h3 extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "4.2.3"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-h3
        package = "4.2.3-4.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-h3 extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "4.2.3"
      }
    }
  }
}
