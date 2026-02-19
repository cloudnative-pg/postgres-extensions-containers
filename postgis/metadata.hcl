metadata = {
  name                     = "postgis"
  sql_name                 = "postgis"
  image_name               = "postgis-extension"
  licenses = <<-EOT
    Apache-2.0 AND blessing AND BSD-2-Clause AND BSD-3-Clause AND
    BSD-3-Clause-Clear AND BSD-3-Clause-LBNL AND BSD-4-Clause-UC AND
    BSL-1.0 AND CC-BY-3.0 AND CC-BY-4.0 AND CC-BY-SA-3.0 AND cURL AND
    FTL AND GPL-2.0 AND GPL-3.0 AND HDF5 AND HPND-sell-variant AND
    IJG AND Info-ZIP AND ISC AND LGPL-2.1 AND Libpng AND libtiff AND
    MIT AND MIT-Modern-Variant AND MPL-1.1 AND OpenLDAP-2.8 AND
    PostgreSQL AND Spencer-86 AND SPL-1.0 AND Unicode-DFS-2015 AND
    Unlicense AND X11 AND Zlib
  EOT
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
