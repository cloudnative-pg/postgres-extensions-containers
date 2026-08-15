metadata = {
  name                     = "first-last-agg"
  sql_name                 = "first_last_agg"
  image_name               = "first-last-agg"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-first-last-agg
        package = "0.1.4-4-gd63ea3b-9.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-first-last-agg extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.1.4"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-first-last-agg
        package = "0.1.4-4-gd63ea3b-9.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-first-last-agg extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "0.1.4"
      }
    }
  }
}
