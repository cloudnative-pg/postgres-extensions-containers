package main

import (
	"context"

	"dagger/maintenance/internal/dagger"
)

func generateTestingValuesExtensions(ctx context.Context, source *dagger.Directory, metadata *extensionMetadata, extensionImage string) ([]map[string]any, error) {
	var out []map[string]any
	configuration, err := generateExtensionConfiguration(metadata, extensionImage)
	if err != nil {
		return nil, err
	}
	out = append(out, configuration)
	for _, deps := range metadata.RequiredExtensions {
		depsMetadata, parseErr := parseExtensionMetadata(ctx, source.Directory(deps))
		if parseErr != nil {
			return nil, parseErr
		}
		depsConfiguration, extErr := generateExtensionConfiguration(depsMetadata, "")
		if extErr != nil {
			return nil, extErr
		}
		out = append(out, depsConfiguration)

	}
	return out, nil
}

func generateExtensionConfiguration(metadata *extensionMetadata, extensionImage string) (map[string]any, error) {
	targetExtensionImage := extensionImage
	if targetExtensionImage == "" {
		var err error
		targetExtensionImage, err = getDefaultExtensionImage(metadata)
		if err != nil {
			return nil, err
		}
	}
	return map[string]any{
		"name": metadata.Name,
		"image": map[string]string{
			"reference": targetExtensionImage,
		},
		"extension_control_path": metadata.ExtensionControlPath,
		"dynamic_library_path":   metadata.DynamicLibraryPath,
		"ld_library_path":        metadata.LdLibraryPath,
	}, nil
}
