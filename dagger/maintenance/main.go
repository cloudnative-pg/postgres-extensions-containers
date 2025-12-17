// This dagger module provides maintenance utilities for CloudNativePG
// Postgres extension container images tasks

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"maps"
	"path"
	"slices"

	"go.yaml.in/yaml/v3"

	"dagger/maintenance/internal/dagger"
)

type Maintenance struct{}

// Updates the OS dependencies in the system-libs directory for the specified extension(s)
func (m *Maintenance) UpdateOSLibs(
	ctx context.Context,
	// The source directory containing the extension folders. Defaults to the current directory
	// +ignore=["dagger", ".github"]
	// +defaultPath="/"
	source *dagger.Directory,
	// The target extension to update OS libs for. Defaults to "all".
	// +default="all"
	target string,
) (*dagger.Directory, error) {
	extDir := source
	if target != "all" {
		extDir = source.Filter(dagger.DirectoryFilterOpts{
			Include: []string{path.Join(target, "**")},
		})
		hasMetadataFile, err := extDir.Exists(ctx, path.Join(target, metadataFile))
		if err != nil {
			return nil, err
		}
		if !hasMetadataFile {
			return nil, fmt.Errorf("not a valid target, metadata.hcl file is missing. Target: %s", target)
		}
	}

	targetExtensions, err := getExtensions(ctx, extDir, WithOSLibsFilter())
	if err != nil {
		return source, err
	}
	if len(targetExtensions) == 0 && target != "all" {
		return nil, fmt.Errorf("the target %q does not require OS Libs update", target)
	}

	const systemLibsDir = "system-libs"
	includeDirs := make([]string, 0, len(targetExtensions))

	for dir, extension := range targetExtensions {
		targetDir := path.Join(dir, systemLibsDir)
		includeDirs = append(includeDirs, targetDir)

		matrix, err := parseBuildMatrix(ctx, source, dir)
		if err != nil {
			return nil, err
		}

		files := make([]*dagger.File, 0, len(matrix.Distributions)*len(matrix.MajorVersions))
		for _, distribution := range matrix.Distributions {
			for _, majorVersion := range matrix.MajorVersions {
				file, err := updateOSLibsOnTarget(
					ctx,
					extension,
					distribution,
					majorVersion,
				)
				if err != nil {
					return source, err
				}
				files = append(files, file)
			}
		}
		source = source.WithFiles(targetDir, files)
	}

	return source.Filter(dagger.DirectoryFilterOpts{
		Include: includeDirs,
	}), nil
}

// Retrieves a list in JSON format of the extensions requiring OS libs updates
func (m *Maintenance) GetOSLibsTargets(
	ctx context.Context,
	// The source directory containing the extension folders. Defaults to the current directory
	// +ignore=["dagger", ".github"]
	// +defaultPath="/"
	source *dagger.Directory,
) (string, error) {
	targetExtensions, err := getExtensions(ctx, source, WithOSLibsFilter())
	if err != nil {
		return "", err
	}
	jsonTargets, err := json.Marshal(slices.Sorted(maps.Keys(targetExtensions)))
	if err != nil {
		return "", err
	}

	return string(jsonTargets), nil
}

// Retrieves a list in JSON format of the extensions
func (m *Maintenance) GetTargets(
	ctx context.Context,
	// The source directory containing the extension folders. Defaults to the current directory
	// +ignore=["dagger", ".github"]
	// +defaultPath="/"
	source *dagger.Directory,
) (string, error) {
	targetExtensions, err := getExtensions(ctx, source)
	if err != nil {
		return "", err
	}
	jsonTargets, err := json.Marshal(slices.Sorted(maps.Keys(targetExtensions)))
	if err != nil {
		return "", err
	}

	return string(jsonTargets), nil
}

// Generates Chainsaw's testing external values in YAML format
func (m *Maintenance) GenerateTestingValues(
	ctx context.Context,
	// Path to the target extension directory
	target *dagger.Directory,
	// URL reference to the extension image to test [REPOSITORY[:TAG]]
	// +optional
	extensionImage string,
) (*dagger.File, error) {
	metadata, err := parseExtensionMetadata(ctx, target)
	if err != nil {
		return nil, err
	}

	targetExtensionImage := extensionImage
	if targetExtensionImage == "" {
		targetExtensionImage, err = getDefaultExtensionImage(metadata)
		if err != nil {
			return nil, err
		}
	}

	annotations, err := getImageAnnotations(targetExtensionImage)
	if err != nil {
		return nil, err
	}

	pgImage := annotations["io.cloudnativepg.image.base.name"]
	if pgImage == "" {
		return nil, fmt.Errorf(
			"extension image %s doesn't have an 'io.cloudnativepg.image.base.name' annotation",
			targetExtensionImage)
	}

	version := annotations["org.opencontainers.image.version"]
	if version == "" {
		return nil, fmt.Errorf(
			"extension image %s doesn't have an 'org.opencontainers.image.version' annotation",
			targetExtensionImage)
	}

	// Build values.yaml content
	values := map[string]any{
		"name":                     metadata.Name,
		"sql_name":                 metadata.SQLName,
		"image_name":               metadata.ImageName,
		"shared_preload_libraries": metadata.SharedPreloadLibraries,
		"extension_control_path":   metadata.ExtensionControlPath,
		"dynamic_library_path":     metadata.DynamicLibraryPath,
		"ld_library_path":          metadata.LdLibraryPath,
		"extension_image":          targetExtensionImage,
		"pg_image":                 pgImage,
		"version":                  version,
	}
	valuesYaml, err := yaml.Marshal(values)
	if err != nil {
		return nil, err
	}

	result := target.WithNewFile("values.yaml", string(valuesYaml))

	return result.File("values.yaml"), nil
}
