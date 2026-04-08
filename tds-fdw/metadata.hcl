metadata = {
  name                     = "tds-fdw"
  sql_name                 = "tds_fdw"
  image_name               = "tds-fdw-extension"
  licenses                 = [ "GPL-2.0-or-later", "MIT", "LGPL-2.1-or-later",
                               "GPL-3.0-or-later", "Apache-2.0", "PostgreSQL", "Zlib" ]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = ["system"]
  bin_path                 = []
  env                      = {
    "GDAL_DATA" = "$${image_root}/share/gdal",
    "PROJ_DATA" = "$${image_root}/share/proj",
  }
  auto_update_os_libs      = true
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: suite=bookworm-pgdg depName=postgresql-18-tds-fdw
        package = "2.0.5-1.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-tds-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.0.5"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-tds-fdw
        package = "2.0.5-1.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-tds-fdw extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "2.0.5"
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
}
