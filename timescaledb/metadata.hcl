metadata = {
  name                     = "timescaledb"
  sql_name                 = "timescaledb"
  image_name               = "timescaledb"
  shared_preload_libraries = ["timescaledb"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false

  versions = {
    bookworm = {
      // renovate: datasource=postgresql depName=timescaledb-2-oss-postgresql-18 versioning=deb
      "18" = "2.24.0~debian12-1801"
    }
    trixie = {
      // renovate: datasource=postgresql depName=timescaledb-2-oss-postgresql-18 versioning=deb
      "18" = "2.24.0~debian13-1801"
    }
  }
}
