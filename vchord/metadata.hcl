metadata = {
  name                     = "vchord"
  sql_name                 = "vchord"
  image_name               = "vchord"
  licenses                 = ["AGPL-3.0-only OR Elastic-2.0"]
  shared_preload_libraries = ["vchord"]
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false
  required_extensions      = ["pgvector"]
  create_extension         = true

  versions = {
    bookworm = {
      // renovate: datasource=github-releases depName=tensorchord/VectorChord versioning=semver extractVersion=^v(?<version>.*)$
      "18" = "1.1.1"
    }
    trixie = {
      // renovate: datasource=github-releases depName=tensorchord/VectorChord versioning=semver extractVersion=^v(?<version>.*)$
      "18" = "1.1.1"
    }
  }
}
