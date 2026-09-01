metadata = {
  name                     = "pglinter"
  sql_name                 = "pglinter"
  image_name               = "pglinter"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-pglinter
      "18" = "2.0.0"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-pglinter
      "18" = "2.0.0"
    }
  }
}
