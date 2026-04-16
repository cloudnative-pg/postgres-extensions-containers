metadata = {
  name                     = "pg-jsonschema"
  sql_name                 = "pg_jsonschema"
  image_name               = "pg-jsonschema"
  licenses                 = ["Apache-2.0"]
  shared_preload_libraries = []
  postgresql_parameters    = {}
  extension_control_path   = []
  dynamic_library_path     = []
  ld_library_path          = []
  bin_path                 = []
  env                      = {}
  auto_update_os_libs      = false
  required_extensions      = []
  create_extension         = true

  versions = {
    bookworm = {
      "18" = {
        // renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
        package = "0.3.4"
        // renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
        sql     = "0.3.4"
      }
    }
    trixie = {
      "18" = {
        // renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
        package = "0.3.4"
        // renovate: datasource=github-tags depName=supabase/pg_jsonschema versioning=semver extractVersion=^v(?<version>.*)$
        sql     = "0.3.4"
      }
    }
  }
}
