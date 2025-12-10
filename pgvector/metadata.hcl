metadata = {
  name                     = "pgvector"
  sql_name                 = "vector"
  image_name               = "pgvector"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-pgvector
      "18" = "0.8.1-2.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-pgvector
      "18" = "0.8.1-2.pgdg13+1"
    }
  }
}
