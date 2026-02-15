package main

import (
	"bytes"
	"context"
	"fmt"
	"path/filepath"
	"slices"

	"go.yaml.in/yaml/v3"

	"dagger/maintenance/internal/dagger"
)

const (
	LabelImageOS   = "images.cnpg.io/os"
	LabelImageType = "images.cnpg.io/type"
)

type ImageVolumeSource struct {
	Reference  string `yaml:"reference"`
	PullPolicy string `yaml:"pullPolicy,omitempty"`
}

type ExtensionConfiguration struct {
	Name                 string            `yaml:"name"`
	ImageVolumeSource    ImageVolumeSource `yaml:"image"`
	ExtensionControlPath []string          `yaml:"extension_control_path,omitempty"`
	DynamicLibraryPath   []string          `yaml:"dynamic_library_path,omitempty"`
	LdLibraryPath        []string          `yaml:"ld_library_path,omitempty"`
}

type ImageCatalog struct {
	APIVersion string `yaml:"apiVersion"`
	Kind       string `yaml:"kind"`
	Metadata   struct {
		Name   string            `yaml:"name"`
		Labels map[string]string `yaml:"labels"`
	} `yaml:"metadata"`
	Spec struct {
		Images []struct {
			Major      int                      `yaml:"major"`
			Image      string                   `yaml:"image"`
			Extensions []ExtensionConfiguration `yaml:"extensions,omitempty"`
		} `yaml:"images"`
	} `yaml:"spec"`
}

func getMinimalCatalogs(ctx context.Context, catalogsDir *dagger.Directory) ([]*ImageCatalog, error) {
	entries, err := catalogsDir.Entries(ctx)
	if err != nil {
		return nil, err
	}

	var catalogs []*ImageCatalog

	for _, entry := range entries {
		if ext := filepath.Ext(entry); ext != ".yaml" && ext != ".yml" {
			continue
		}

		content, err := catalogsDir.File(entry).Contents(ctx)
		if err != nil {
			return nil, fmt.Errorf("while retrieving %s: %w", entry, err)
		}

		var catalog ImageCatalog
		if err := yaml.Unmarshal([]byte(content), &catalog); err != nil {
			return nil, fmt.Errorf("while decoding %s: %w", entry, err)
		}

		// Only keep ClusterImageCatalogs
		if catalog.Kind != "ClusterImageCatalog" {
			continue
		}

		// Only keep catalogs with minimal images
		if catalog.Metadata.Labels[LabelImageType] != "minimal" {
			continue
		}

		// Only keep catalogs for Supported Distros
		catalogOS, ok := catalog.Metadata.Labels[LabelImageOS]
		if !ok {
			return nil, fmt.Errorf("while retrieving OS for %q catalog", entry)
		}
		if !slices.Contains(SupportedDistributions, catalogOS) {
			continue
		}

		catalogs = append(catalogs, &catalog)
	}

	return catalogs, nil
}

func writeCatalogToDir(catalog *ImageCatalog, outDir *dagger.Directory) (*dagger.Directory, error) {
	var buf bytes.Buffer
	enc := yaml.NewEncoder(&buf)
	enc.SetIndent(2)

	if err := enc.Encode(catalog); err != nil {
		return nil, fmt.Errorf("while encoding catalog %s: %w", catalog.Metadata.Name, err)
	}
	if err := enc.Close(); err != nil {
		return nil, err
	}

	outName := fmt.Sprintf("catalog-extensions-%s.yaml", catalog.Metadata.Labels[LabelImageOS])

	return outDir.WithNewFile(outName, buf.String()), nil
}
