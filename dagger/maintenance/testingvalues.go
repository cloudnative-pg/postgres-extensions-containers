package main

import (
	"context"
	"fmt"

	"dagger/maintenance/internal/dagger"
)

type ExtensionSpec struct {
	Ensure  string `yaml:"ensure"`
	Name    string `yaml:"name"`
	Version string `yaml:"version"`
}

type ExpectedStatus struct {
	Applied bool   `yaml:"applied"`
	Name    string `yaml:"name"`
}

type DatabaseConfig struct {
	ExtensionsSpec []ExtensionSpec  `yaml:"extensions_spec"`
	ExpectedStatus []ExpectedStatus `yaml:"expected_status"`
}

type TestingValues struct {
	Name                   string                    `yaml:"name"`
	SQLName                string                    `yaml:"sql_name"`
	SharedPreloadLibraries []string                  `yaml:"shared_preload_libraries"`
	PgImage                string                    `yaml:"pg_image"`
	Version                string                    `yaml:"version"`
	Extensions             []*ExtensionConfiguration `yaml:"extensions"`
	DatabaseConfig         *DatabaseConfig           `yaml:"database_config"`
}

func generateTestingValuesExtensions(ctx context.Context, source *dagger.Directory, metadata *extensionMetadata, extensionImage string) ([]*ExtensionConfiguration, error) {
	var out []*ExtensionConfiguration
	configuration, err := generateExtensionConfiguration(metadata, extensionImage)
	if err != nil {
		return nil, err
	}
	out = append(out, configuration)

	for _, dep := range metadata.RequiredExtensions {
		depExists, err := source.Exists(ctx, dep)
		if err != nil {
			return nil, err
		}
		if !depExists {
			return nil, fmt.Errorf("required dependency %q not found", dep)
		}

		depMetadata, err := parseExtensionMetadata(ctx, source.Directory(dep))
		if err != nil {
			return nil, fmt.Errorf("failed to parse dependency metadata %q: %w", dep, err)
		}
		depConfiguration, err := generateExtensionConfiguration(depMetadata, "")
		if err != nil {
			return nil, err
		}
		out = append(out, depConfiguration)
	}

	return out, nil
}

func generateExtensionConfiguration(metadata *extensionMetadata, extensionImage string) (*ExtensionConfiguration, error) {
	targetExtensionImage := extensionImage
	if targetExtensionImage == "" {
		var err error
		targetExtensionImage, err = getDefaultExtensionImage(metadata)
		if err != nil {
			return nil, err
		}
	}

	return &ExtensionConfiguration{
		Name: metadata.Name,
		ImageVolumeSource: ImageVolumeSource{
			Reference: targetExtensionImage,
		},
		ExtensionControlPath: metadata.ExtensionControlPath,
		DynamicLibraryPath:   metadata.DynamicLibraryPath,
		LdLibraryPath:        metadata.LdLibraryPath,
	}, nil
}

func generateDatabaseConfig(ctx context.Context, source *dagger.Directory, extensionsConfig []*ExtensionConfiguration) (*DatabaseConfig, error) {
	var databaseConfig DatabaseConfig
	for _, extension := range extensionsConfig {
		extMetadata, err := parseExtensionMetadata(ctx, source.Directory(extension.Name))
		if err != nil {
			return nil, fmt.Errorf("failed to parse dependency metadata %q: %w", extension.Name, err)
		}

		extAnnotations, err := getImageAnnotations(extension.ImageVolumeSource.Reference)
		if err != nil {
			return nil, err
		}

		extVersion := extAnnotations["org.opencontainers.image.version"]
		if extVersion == "" {
			return nil, fmt.Errorf(
				"extension image %s doesn't have an 'org.opencontainers.image.version' annotation",
				extension.ImageVolumeSource.Reference)
		}

		ensureOption := "absent"
		if extMetadata.CreateExtension {
			ensureOption = "present"
		}

		databaseConfig.ExtensionsSpec = append(databaseConfig.ExtensionsSpec,
			ExtensionSpec{
				Ensure:  ensureOption,
				Name:    extMetadata.SQLName,
				Version: extVersion,
			},
		)
		databaseConfig.ExpectedStatus = append(databaseConfig.ExpectedStatus,
			ExpectedStatus{
				Name:    extMetadata.SQLName,
				Applied: true,
			},
		)
	}

	return &databaseConfig, nil
}
