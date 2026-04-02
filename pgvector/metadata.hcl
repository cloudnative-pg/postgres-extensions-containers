metadata = {
  name                     = "pgvector"
  sql_name                 = "vector"
  image_name               = "pgvector"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgvector
        package = "0.8.2-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-pgvector extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.8.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgvector
        package = "0.8.2-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-pgvector extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.8.2"
      }
    }
  }
}
