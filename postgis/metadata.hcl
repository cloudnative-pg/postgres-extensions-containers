metadata = {
  name                     = "postgis"
  sql_name                 = "postgis"
  image_name               = "postgis-extension"
  licenses                 = [ "Apache-2.0", "blessing", "BSD-2-Clause", "BSD-3-Clause",
                              "BSD-3-Clause-Clear", "BSD-3-Clause-LBNL", "BSD-4-Clause-UC",
                              "BSL-1.0", "CC-BY-3.0", "CC-BY-4.0", "CC-BY-SA-3.0", "curl",
                              "FTL", "GPL-2.0-or-later", "GPL-3.0-or-later", "HDF5", "HPND-sell-variant",
                              "IJG", "Info-ZIP", "ISC", "LGPL-2.1-or-later", "Libpng", "libtiff",
                              "MIT", "MIT-Modern-Variant", "MPL-1.1", "OLDAP-2.8",
                              "PostgreSQL", "Spencer-86", "SPL-1.0", "Unicode-DFS-2015",
                              "Unlicense", "X11", "Zlib" ]
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
