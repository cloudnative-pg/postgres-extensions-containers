metadata = {
  name                     = "pgaudit"
  sql_name                 = "pgaudit"
  image_name               = "pgaudit"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = ["pgaudit"]
  postgresql_parameters    = {}
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgaudit
        package = "18.0-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgaudit extractVersion=^(?<version>\d+\.\d+)
        sql     = "18.0"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgaudit
        package = "18.0-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgaudit extractVersion=^(?<version>\d+\.\d+)
        sql     = "18.0"
      }
    }
  }
}
