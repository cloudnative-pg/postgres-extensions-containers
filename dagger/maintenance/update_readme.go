package main

import (
	"context"
	"dagger/maintenance/internal/dagger"
	"errors"
	"fmt"
	"path"
	"regexp"
)

const readmeFilename = "README.md"

func updateReadme(ctx context.Context, target *dagger.Directory) (*dagger.File, error) {
	metadata, err := parseExtensionMetadata(ctx, target)
	if err != nil {
		return nil, err
	}
	extImage, extImageErr := getDefaultExtensionImage(metadata)
	if extImageErr != nil {
		return nil, extImageErr
	}
	readmeFile := target.File(readmeFilename)
	if readmeFile == nil {
		return nil, errors.New("README file not found")
	}

	readmeContent, contentErr := readmeFile.Contents(ctx)
	if contentErr != nil {
		return nil, contentErr
	}
	searchPattern := fmt.Sprintf(
		`(ghcr\.io\/cloudnative-pg\/%s:)(\d+(?:\.\d+)+)-%d-%s`,
		metadata.Name,
		DefaultPgMajor,
		DefaultDistribution,
	)

	re := regexp.MustCompile(searchPattern)

	newContent := re.ReplaceAllString(readmeContent, extImage)

	out := target.WithNewFile(readmeFilename, newContent)

	return out.File(readmeFilename), nil

}

func extensionsWithReadme(
	ctx context.Context,
	source *dagger.Directory,
) (map[string]string, error) {
	dirs, err := extensionsDirectories(ctx, source)
	if err != nil {
		return nil, err
	}

	extensions := make(map[string]string)
	for _, dir := range dirs {
		metadata, err := parseExtensionMetadata(ctx, dir)
		if err != nil {
			return nil, err
		}
		dirName, err := dir.Name(ctx)
		if err != nil {
			return nil, err
		}
		exists, existsErr := dir.Exists(ctx, readmeFilename)
		if existsErr == nil && exists {
			extensions[path.Dir(dirName)] = metadata.Name
		}
	}

	return extensions, nil
}
