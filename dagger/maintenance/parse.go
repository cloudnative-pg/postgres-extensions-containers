package main

import (
	"context"
	"encoding/json"
	"path"

	"github.com/docker/buildx/bake"
	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclsimple"

	"dagger/maintenance/internal/dagger"
)

type buildMatrix struct {
	Distributions []string
	MajorVersions []string
}

type extensionMetadata struct {
	Name             string   `hcl:"name" cty:"name"`
	AutoUpdateOsLibs bool     `hcl:"auto_update_os_libs" cty:"auto_update_os_libs"`
	Remain           hcl.Body `hcl:",remain"`
}

const (
	bakeFileName = "docker-bake.hcl"
	metadataFile = "metadata.hcl"
)

func parseBuildMatrix(ctx context.Context, source *dagger.Directory, target string) (*buildMatrix, error) {
	bakeData, err := source.File(bakeFileName).Contents(ctx)
	if err != nil {
		return nil, err
	}
	metadata, err := source.File(path.Join(target, metadataFile)).Contents(ctx)
	if err != nil {
		return nil, err
	}
	_, p, err := bake.ParseFiles([]bake.File{
		{
			Name: bakeFileName,
			Data: []byte(bakeData),
		},
		{
			Name: metadataFile,
			Data: []byte(metadata),
		},
	}, nil)
	if err != nil {
		return nil, err
	}

	var matrix buildMatrix
	for _, variable := range p.AllVariables {
		switch variable.Name {
		case "distributions":
			if variable.Value != nil {
				var arr []string
				if err := json.Unmarshal([]byte(*variable.Value), &arr); err != nil {
					return nil, err
				}
				matrix.Distributions = arr
			}
		case "pgVersions":
			if variable.Value != nil {
				var arr []string
				if err := json.Unmarshal([]byte(*variable.Value), &arr); err != nil {
					return nil, err
				}
				matrix.MajorVersions = arr
			}
		}
	}

	return &matrix, nil
}

func parseExtensionMetadata(ctx context.Context, extensionDirectory *dagger.Directory) (*extensionMetadata, error) {
	type Config struct {
		Metadata extensionMetadata `hcl:"metadata"`
		Remain   hcl.Body          `hcl:",remain"`
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
