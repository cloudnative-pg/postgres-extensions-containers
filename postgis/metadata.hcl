metadata = {
  name                     = "postgis"
  sql_name                 = "postgis"
  image_name               = "postgis-extension"
  licenses                 = [ "GPL-2.0-or-later", "MIT", "LGPL-2.1-or-later",
                               "GPL-3.0-or-later", "Apache-2.0", "PostgreSQL", "Zlib" ]
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      // renovate: suite=bookworm-pgdg depName=postgresql-18-postgis-3
      "18" = "3.6.2+dfsg-1.pgdg12+1"
    }
    trixie = {
      // renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
      "18" = "3.6.2+dfsg-1.pgdg13+1"
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
