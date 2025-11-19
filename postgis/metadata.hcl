metadata = {
  name                     = "postgis"
  sql_name                 = "postgis"
  image_name               = "postgis-extension"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["/system"]
  major_version            = "3"

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-postgis-3
      "18" = "3.6.0+dfsg-3.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
      "18" = "3.6.0+dfsg-3.pgdg13+1"
    }
  }
}
