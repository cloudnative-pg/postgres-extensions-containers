// This dagger module provides maintenance utilities for CloudNativePG
// Postgres extension container images tasks

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"maps"
	"path"
	"regexp"
	"slices"
	"sort"
	"strconv"
	"strings"
	"text/template"
	"time"

	"go.yaml.in/yaml/v3"
	"golang.org/x/text/cases"
	"golang.org/x/text/language"

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
	// The source directory containing the extension folders. Defaults to the current directory
	// +ignore=["dagger", ".github"]
	// +defaultPath="/"
	source *dagger.Directory,
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

	extensions, err := generateTestingValuesExtensions(ctx, source, metadata, targetExtensionImage)
	if err != nil {
		return nil, err
	}

	// Build values.yaml content
	values := map[string]any{
		"name":                     metadata.Name,
		"sql_name":                 metadata.SQLName,
		"shared_preload_libraries": metadata.SharedPreloadLibraries,
		"pg_image":                 pgImage,
		"version":                  version,
		"extensions":               extensions,
	}
	valuesYaml, err := yaml.Marshal(values)
	if err != nil {
		return nil, err
	}

	result := target.WithNewFile("values.yaml", string(valuesYaml))

	return result.File("values.yaml"), nil
}

// Scaffolds a new Postgres extension directory structure
func (m *Maintenance) Create(
	ctx context.Context,
	// The source directory containing the extension template files
	// +defaultPath="/templates"
	templatesDir *dagger.Directory,
	// The name of the extension
	name string,
	// The Postgres major versions the extension is supported for
	// +default=["18"]
	versions []string,
	// The Debian distributions the extension is supported for
	// +default=["trixie","bookworm"]
	distros []string,
	// The Debian package name for the extension. If the package name contains
	// the postgres version, it can be templated using the "%version%" placeholder.
	//  (default "postgresql-%version%-<name>")
	// +optional
	packageName string,
) (*dagger.Directory, error) {
	// Validate name parameter
	if name == "" {
		return nil, fmt.Errorf("name cannot be empty")
	}
	// Validate name contains only lowercase alphanumeric characters, hyphens, and underscores
	validNamePattern := regexp.MustCompile(`^[a-z0-9_-]+$`)
	if !validNamePattern.MatchString(name) {
		return nil, fmt.Errorf(
			"invalid extension name: %s (must contain only lowercase alphanumeric characters, hyphens, and underscores)",
			name,
		)
	}

	// Validate versions array is not empty
	if len(versions) == 0 {
		return nil, fmt.Errorf("versions array cannot be empty")
	}

	// Validate distros array is not empty
	if len(distros) == 0 {
		return nil, fmt.Errorf("distros array cannot be empty")
	}

	// Validate template files exist
	var templateFiles = []string{
		"metadata.hcl",
		"Dockerfile",
		"README.md",
	}
	for _, fileName := range templateFiles {
		tmplFile := templatesDir.File(fileName + ".tmpl")
		if _, err := tmplFile.Contents(ctx); err != nil {
			return nil, fmt.Errorf("required template file %s.tmpl not found: %w", fileName, err)
		}
	}

	extDir := dag.Directory()

	type Extension struct {
		Name           string
		Versions       []string
		Distros        []string
		Package        string
		DefaultVersion int
		DefaultDistro  string
	}

	if packageName == "" {
		packageName = "postgresql-%version%-" + name
	}

	extension := Extension{
		Name:           name,
		Versions:       versions,
		Distros:        distros,
		Package:        packageName,
		DefaultVersion: DefaultPgMajor,
		DefaultDistro:  DefaultDistribution,
	}

	toTitle := func(s string) string {
		return cases.Title(language.English).String(s)
	}

	funcMap := template.FuncMap{
		"replaceAll": strings.ReplaceAll,
		"toTitle":    toTitle,
	}

	executeTemplate := func(fileName string) error {
		tmplFile := templatesDir.File(fileName + ".tmpl")
		tmplContent, err := tmplFile.Contents(ctx)
		if err != nil {
			return fmt.Errorf("failed to read template file %s.tmpl: %w", fileName, err)
		}
		tmpl, err := template.New(fileName).Funcs(funcMap).Parse(tmplContent)
		if err != nil {
			return fmt.Errorf("failed to parse template %s.tmpl: %w", fileName, err)
		}
		buf := &bytes.Buffer{}
		if err := tmpl.Execute(buf, extension); err != nil {
			return fmt.Errorf("failed to execute template %s.tmpl: %w", fileName, err)
		}
		extDir = extDir.WithNewFile(fileName, buf.String())
		return nil
	}

	for _, fileName := range templateFiles {
		if err := executeTemplate(fileName); err != nil {
			return nil, err
		}
	}

	return extDir, nil
}

// Tests the specified target using Chainsaw
func (m *Maintenance) Test(
	ctx context.Context,
	// The source directory containing the extension folders. Defaults to the current directory
	// +ignore=["dagger", ".github"]
	// +defaultPath="/"
	source *dagger.Directory,
	// Kubeconfig to connect to the target K8s
	// +required
	kubeconfig *dagger.File,
	// The target extension to test
	// +default="all"
	target string,
	// Container image to use to run chainsaw
	// renovate: datasource=docker depName=kyverno/chainsaw packageName=ghcr.io/kyverno/chainsaw versioning=docker
	// +default="ghcr.io/kyverno/chainsaw:v0.2.14@sha256:c703e4d4ce7b89c5121fe957ab89b6e2d33f91fd15f8274a9f79ca1b2ba8ecef"
	chainsawImage string,
) error {
	extDir := source
	if target != "all" {
		extDir = source.Filter(dagger.DirectoryFilterOpts{
			Include: []string{path.Join(target, "**"), "test"},
		})
		hasMetadataFile, err := extDir.Exists(ctx, path.Join(target, metadataFile))
		if err != nil {
			return err
		}
		if !hasMetadataFile {
			return fmt.Errorf("not a valid target, metadata.hcl file is missing. Target: %s", target)
		}
	}

	targetExtensions, err := extensionsDirectories(ctx, extDir)
	if err != nil {
		return err
	}

	const valuesFile = "values.yaml"

	for _, targetExtension := range targetExtensions {
		extName, err := targetExtension.Name(ctx)
		if err != nil {
			return err
		}

		hasValues, err := targetExtension.Exists(ctx, valuesFile)
		if err != nil {
			return err
		}
		if !hasValues {
			return fmt.Errorf("cannot execute tests for extension %q, values.yaml file is missing", target)
		}

		ctr := dag.Container().From(chainsawImage).
			WithWorkdir("e2e").
			WithEnvVariable("CACHEBUSTER", time.Now().String()).
			WithDirectory("test", extDir.Directory("test")).
			WithDirectory(extName, targetExtension).
			WithFile("/etc/kubeconfig/config", kubeconfig).
			WithEnvVariable("KUBECONFIG", "/etc/kubeconfig/config")

		_, err = ctr.WithExec(
			[]string{"test", "./test", "--values", path.Join(extName, valuesFile)},
			dagger.ContainerWithExecOpts{
				UseEntrypoint: true,
			}).
			Sync(ctx)

		if err != nil {
			return err
		}

		hasIndividualTests, err := targetExtension.Exists(ctx, "test")
		if err != nil {
			return err
		}
		if !hasIndividualTests {
			continue
		}
		_, err = ctr.WithExec(
			[]string{"test", path.Join(extName, "test"), "--values", path.Join(extName, valuesFile)},
			dagger.ContainerWithExecOpts{
				UseEntrypoint: true,
			}).
			Sync(ctx)
		if err != nil {
			return err
		}
	}

	return nil
}

// Generate extension's ClusterImageCatalogs starting from a base set of catalogs
func (m *Maintenance) GenerateCatalogs(
	ctx context.Context,
	// The source directory containing the extension folders. Defaults to the current directory
	// +ignore=["dagger", ".github"]
	// +defaultPath="/"
	source *dagger.Directory,
	// The directory containing the starting catalogs. Defaults to "/image-catalogs"
	// +defaultPath="/image-catalogs"
	catalogsDir *dagger.Directory,
) (*dagger.Directory, error) {
	outDir := dag.Directory()

	catalogs, err := getMinimalCatalogs(ctx, catalogsDir)
	if err != nil {
		return nil, fmt.Errorf("while retrieving base catalogs: %w", err)
	}

	targetExtensions, err := getExtensions(ctx, source)
	if err != nil {
		return nil, fmt.Errorf("while retrieving extensions: %w", err)
	}
	if len(targetExtensions) == 0 {
		return nil, fmt.Errorf("no extensions found in source directory")
	}

	catalogWritten := false
	for _, catalog := range catalogs {
		catalogOS, ok := catalog.Metadata.Labels[LabelImageOS]
		if !ok {
			return nil, fmt.Errorf("while retrieving OS for %q catalog", catalog.Metadata.Name)
		}

		for dir, extension := range targetExtensions {
			matrix, err := parseBuildMatrix(ctx, source, dir)
			if err != nil {
				return nil, fmt.Errorf("while parsing build Matrix for extension %s: %w", extension, err)
			}
			if !slices.Contains(matrix.Distributions, catalogOS) {
				continue
			}

			metadata, err := parseExtensionMetadata(ctx, source.Directory(dir))
			if err != nil {
				return nil, fmt.Errorf("while parsing extension %s metadata: %w", extension, err)
			}

			for i := range catalog.Spec.Images {
				img := &catalog.Spec.Images[i]
				if !slices.Contains(matrix.MajorVersions, strconv.Itoa(img.Major)) {
					continue
				}

				targetExtensionImage, err := getExtensionImageWithTimestamp(metadata, catalogOS, img.Major)
				if err != nil {
					return nil, fmt.Errorf("while retrieving extension %s image: %w", extension, err)
				}

				extensionsConfig := ExtensionConfiguration{
					Name: metadata.Name,
					ImageVolumeSource: ImageVolumeSource{
						Reference: targetExtensionImage,
					},
					ExtensionControlPath: metadata.ExtensionControlPath,
					DynamicLibraryPath:   metadata.DynamicLibraryPath,
					LdLibraryPath:        metadata.LdLibraryPath,
				}

				img.Extensions = append(img.Extensions, extensionsConfig)

				// Sort extensions by name
				sort.Slice(img.Extensions, func(i, j int) bool {
					return img.Extensions[i].Name < img.Extensions[j].Name
				})
			}
		}

		outDir, err = writeCatalogToDir(catalog, outDir)
		if err != nil {
			return nil, fmt.Errorf("while writing catalog %s: %w", catalog.Metadata.Name, err)
		}
		catalogWritten = true
	}

	if !catalogWritten {
		return nil, fmt.Errorf("no catalogs matched the selection criteria")
	}

	return outDir, nil
}
