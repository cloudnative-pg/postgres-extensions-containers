metadata = {
  name                     = "pgaudit"
  sql_name                 = "pgaudit"
  image_name               = "pgaudit"
  shared_preload_libraries = ["pgaudit"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-pgaudit
      "18" = "18.0-2.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-pgaudit
      "18" = "18.0-2.pgdg13+1"
    }
  }
}
