metadata = {
  name                     = "pg_ivm"
  sql_name                 = "pg_ivm"
  image_name               = "pg_ivm"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []

  versions = {
    bookworm = {
      // pg_ivm version from GitHub releases
      "18" = "1.13"
    }
    trixie = {
      // pg_ivm version from GitHub releases
      "18" = "1.13"
    }
  }
}