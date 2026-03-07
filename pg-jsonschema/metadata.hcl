metadata = {
  name                     = "pg-jsonschema"
  sql_name                 = "pg_jsonschema"
  image_name               = "pg-jsonschema"
  shared_preload_libraries = []
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  auto_update_os_libs      = false
  required_extensions      = []

  versions = {
    bookworm = {
      // renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
      "18" = "0.3.4"
    }
    trixie = {
      // renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
      "18" = "0.3.4"
    }
  }
}
