metadata = {
  name                     = "postgis"
  sql_name                 = "postgis"
  image_name               = "postgis-extension"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["/system"]
  auto_update_os_libs      = true

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-postgis-3
      "18" = "3.6.1+dfsg-1.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
      "18" = "3.6.1+dfsg-1.pgdg13+1"
    }
  }
}

target "default" {
  name = "${metadata.name}-${sanitize(getExtensionVersion(distro, pgVersion))}-${pgVersion}-${distro}"
  matrix = {
    pgVersion = pgVersions
    distro = distributions
  }

  args = {
    POSTGIS_MAJOR = "3"
  }
}
