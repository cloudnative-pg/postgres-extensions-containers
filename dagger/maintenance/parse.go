package main

import (
	"cmp"
	"context"
	"fmt"
	"slices"

	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclsimple"

	"dagger/maintenance/internal/dagger"
)

// buildMatrix is the set of distribution/PG-major combinations to build.
// It holds explicit pairs (rather than two independent lists), so each distribution
// can declare its own set of PG majors.
type buildMatrix struct {
	Combinations []buildCombo
}

// buildCombo is a single distribution + PG major combination to build.
type buildCombo struct {
	Distribution string
	MajorVersion string
}

// hasDistribution reports if given a distribution is present in a buildMatrix.
func (m *buildMatrix) hasDistribution(distribution string) bool {
	return slices.ContainsFunc(m.Combinations, func(combo buildCombo) bool {
		return combo.Distribution == distribution
	})
}

// contains reports if a given distribution/major pair is present in a buildMatrix.
func (m *buildMatrix) contains(distribution, majorVersion string) bool {
	return slices.ContainsFunc(m.Combinations, func(combo buildCombo) bool {
		return combo.Distribution == distribution && combo.MajorVersion == majorVersion
	})
}

type extensionVersion struct {
	Package string `hcl:"package" cty:"package"`
}

type versionMap map[string]map[string]extensionVersion

type extensionMetadata struct {
	Name                   string            `hcl:"name" cty:"name"`
	SQLName                string            `hcl:"sql_name" cty:"sql_name"`
	ImageName              string            `hcl:"image_name" cty:"image_name"`
	SharedPreloadLibraries []string          `hcl:"shared_preload_libraries" cty:"shared_preload_libraries"`
	PostgresqlParameters   map[string]string `hcl:"postgresql_parameters" cty:"postgresql_parameters"`
	ExtensionControlPath   []string          `hcl:"extension_control_path" cty:"extension_control_path"`
	DynamicLibraryPath     []string          `hcl:"dynamic_library_path" cty:"dynamic_library_path"`
	LdLibraryPath          []string          `hcl:"ld_library_path" cty:"ld_library_path"`
	BinPath                []string          `hcl:"bin_path" cty:"bin_path"`
	Env                    map[string]string `hcl:"env" cty:"env"`
	AutoUpdateOsLibs       bool              `hcl:"auto_update_os_libs" cty:"auto_update_os_libs"`
	RequiredExtensions     []string          `hcl:"required_extensions" cty:"required_extensions"`
	CreateExtension        bool              `hcl:"create_extension" cty:"create_extension"`
	Versions               versionMap        `hcl:"versions" cty:"versions"`
	Remain                 hcl.Body          `hcl:",remain"`
}

const (
	metadataFile = "metadata.hcl"
)

// parseBuildMatrix derives the build matrix for a target extension by reading
// its metadata.hcl from the source directory.
func parseBuildMatrix(ctx context.Context, source *dagger.Directory, target string) (*buildMatrix, error) {
	metadata, err := parseExtensionMetadata(ctx, source.Directory(target))
	if err != nil {
		return nil, err
	}

	return buildMatrixFromMetadata(metadata), nil
}

// buildMatrixFromMetadata derives the build matrix (distributions and PG majors)
// directly from the keys of the metadata.versions map, mirroring how the
// docker-bake.hcl matrix is computed.
func buildMatrixFromMetadata(metadata *extensionMetadata) *buildMatrix {
	var matrix buildMatrix
	for distribution, versionsByMajor := range metadata.Versions {
		for majorVersion := range versionsByMajor {
			matrix.Combinations = append(matrix.Combinations, buildCombo{
				Distribution: distribution,
				MajorVersion: majorVersion,
			})
		}
	}

	// Sort for deterministic ordering, since map iteration order is random.
	slices.SortFunc(matrix.Combinations, func(a, b buildCombo) int {
		if c := cmp.Compare(a.Distribution, b.Distribution); c != 0 {
			return c
		}
		return cmp.Compare(a.MajorVersion, b.MajorVersion)
	})

	return &matrix
}

func parseExtensionMetadata(ctx context.Context, extensionDirectory *dagger.Directory) (*extensionMetadata, error) {
	type Config struct {
		Metadata extensionMetadata `hcl:"metadata"`
		Remain   hcl.Body          `hcl:",remain"`
	}

	hasMetadataFile, err := extensionDirectory.Exists(ctx, metadataFile)
	if err != nil {
		return nil, err
	}
	if !hasMetadataFile {
		return nil, fmt.Errorf("metadata.hcl file is missing")
	}

	data, err := extensionDirectory.File(metadataFile).Contents(ctx)
	if err != nil {
		return nil, err
	}

	var rootMeta Config
	err = hclsimple.Decode(metadataFile, []byte(data), nil, &rootMeta)
	if err != nil {
		return nil, err
	}

	return &rootMeta.Metadata, nil
}
