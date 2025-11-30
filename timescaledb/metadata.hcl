metadata = {
  name = "timescaledb"
  sql_name = "timescaledb"
  image_name = "timescaledb"
  shared_preload_libraries = ["timescaledb"]
  extension_control_path = []
  dynamic_library_path = []
  ld_library_path = []
  versions = {
    bookworm = {
      // renovate: datasource=postgresql depName=timescaledb-2-postgresql-18 versioning=deb
      "18" = "2.23.1~debian12-1800"
    }
    trixie = {
      // renovate: datasource=postgresql depName=timescaledb-2-postgresql-18 versioning=deb
      "18" = "2.23.1~debian13-1800"
    }
  }
}