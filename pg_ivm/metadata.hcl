metadata = {
  name                     = "pg_ivm"
  sql_name                 = "pg_ivm"
  image_name               = "pg_ivm"
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
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-ivm
        package = "1.13-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pg-ivm extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.13"
      }
    }
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-ivm
        package = "1.13-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pg-ivm extractVersion=^(?<version>\d+\.\d+)
        sql     = "1.13"
      }
    }
  }
}
