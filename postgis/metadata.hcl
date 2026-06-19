metadata = {
  name                     = "postgis"
  sql_name                 = "postgis"
  image_name               = "postgis-extension"
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
        // renovate: suite=bookworm-pgdg depName=postgresql-18-postgis-3
        package = "3.6.4+dfsg-2.pgdg12+1"
        // renovate: suite=bookworm-pgdg depName=postgresql-18-postgis-3 extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "3.6.4"
      }
    }
    trixie = {
      "18" = {
        // renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3
        package = "3.6.4+dfsg-2.pgdg13+1"
        // renovate: suite=trixie-pgdg depName=postgresql-18-postgis-3 extractVersion=^(?<version>\d+\.\d+\.\d+)
        sql     = "3.6.4"
      }
    }
  }
}

// Re-declare name + matrix (matching docker-bake.hcl) so the matrix-expanded
// targets merge by name and pick up the extra POSTGIS_MAJOR build arg.
target "default" {
  name = getBuildName(metadata.name, build.distro, build.pgVersion)
  matrix = {
    build = getBuildMatrix()
  }

  args = {
    POSTGIS_MAJOR = "3"
  }
}
