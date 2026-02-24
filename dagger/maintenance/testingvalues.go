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

type DatabaseConfig struct {
	ExtensionsSpec []ExtensionSpec `yaml:"extensions_spec,omitempty"`
}

type TestingValues struct {
	Name                   string                    `yaml:"name"`
	SQLName                string                    `yaml:"sql_name"`
	SharedPreloadLibraries []string                  `yaml:"shared_preload_libraries"`
	PgImage                string                    `yaml:"pg_image"`
	Version                string                    `yaml:"version"`
	CreateExtension        bool                      `yaml:"create_extension"`
	Extensions             []*ExtensionConfiguration `yaml:"extensions"`
	DatabaseConfig         *DatabaseConfig           `yaml:"database_config"`
	DatabaseAssertStatus   map[string]any            `yaml:"database_assert_status"`
}

type testingExtensionInfo struct {
	Configuration   *ExtensionConfiguration
	SQLName         string
	Version         string
	CreateExtension bool
}

func generateTestingValuesExtensions(ctx context.Context, source *dagger.Directory, metadata *extensionMetadata,
	extensionImage string, version string, registryUsername string, registryPassword *dagger.Secret) ([]*testingExtensionInfo, error) {
	var out []*testingExtensionInfo
	configuration, err := generateExtensionConfiguration(metadata, extensionImage)
	if err != nil {
		return nil, err
	}
	out = append(out, &testingExtensionInfo{
		Configuration:   configuration,
		SQLName:         metadata.SQLName,
		Version:         version,
		CreateExtension: metadata.CreateExtension,
	})

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

		depAnnotations, err := getImageAnnotations(ctx, depConfiguration.ImageVolumeSource.Reference, registryUsername, registryPassword)
		if err != nil {
			return nil, err
		}
		depVersion := depAnnotations["org.opencontainers.image.version"]
		if depVersion == "" {
			return nil, fmt.Errorf(
				"extension image %s doesn't have an 'org.opencontainers.image.version' annotation",
				depConfiguration.ImageVolumeSource.Reference)
		}

		out = append(out, &testingExtensionInfo{
			Configuration:   depConfiguration,
			SQLName:         depMetadata.SQLName,
			Version:         depVersion,
			CreateExtension: depMetadata.CreateExtension,
		})
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

func generateDatabaseConfig(extensionInfos []*testingExtensionInfo) *DatabaseConfig {
	var databaseConfig DatabaseConfig
	for _, info := range extensionInfos {
		if !info.CreateExtension {
			continue
		}

		databaseConfig.ExtensionsSpec = append(databaseConfig.ExtensionsSpec,
			ExtensionSpec{
				Ensure:  "present",
				Name:    info.SQLName,
				Version: info.Version,
			},
		)
	}

	return &databaseConfig
}

func generateDatabaseAssertStatus(extensionInfos []*testingExtensionInfo) map[string]any {
	status := map[string]any{
		"applied":            true,
		"observedGeneration": 1,
	}

	var extensions []map[string]any
	for _, info := range extensionInfos {
		if !info.CreateExtension {
			continue
		}
		extensions = append(extensions, map[string]any{
			"applied": true,
			"name":    info.SQLName,
		})
	}
	if len(extensions) > 0 {
		status["extensions"] = extensions
	}

	return status
}
