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
  bin_path                 = []
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-postgis-3
        package = "3.6.2+dfsg-1.pgdg12+1"
        sql     = "3.6.2"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
        package = "3.6.2+dfsg-1.pgdg13+1"
        sql     = "3.6.2"
      }
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
