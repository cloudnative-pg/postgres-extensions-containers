metadata = {
  name                     = "wal2json"
  sql_name                 = "wal2json"
  image_name               = "wal2json"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-wal2json
      "18" = "2.6-3.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-wal2json
      "18" = "2.6-3.pgdg13+1"
    }
  }
}
