metadata = {
  name                     = "pg-uuidv7"
  sql_name                 = "pg_uuidv7"
  image_name               = "pg-uuidv7"
  licenses                 = ["PostgreSQL"]
  shared_preload_libraries = []
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-uuidv7
        package = "1.7.0-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-uuidv7 extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.7"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-uuidv7
        package = "1.7.0-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-uuidv7 extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.7"
      }
    }
  }
}
