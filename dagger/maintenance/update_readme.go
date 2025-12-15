package main

import (
	"context"
	"errors"
	"fmt"
	"regexp"

	"dagger/maintenance/internal/dagger"
)

const readmeFilename = "README.md"

type updateFunc func(metadata *extensionMetadata, content string) string

var updates = []updateFunc{
	updateExtensionImage,
	updateExtensionVersion,
}

func updateReadme(ctx context.Context, target *dagger.Directory) (*dagger.File, error) {
	metadata, err := parseExtensionMetadata(ctx, target)
	if err != nil {
		return nil, err
	}
	readmeFile := target.File(readmeFilename)
	if readmeFile == nil {
		return nil, errors.New("README file not found")
	}

	readmeContent, contentErr := readmeFile.Contents(ctx)
	if contentErr != nil {
		return nil, contentErr
	}

	for _, upd := range updates {
		readmeContent = upd(metadata, readmeContent)
	}

	out := target.WithNewFile(readmeFilename, readmeContent)

	return out.File(readmeFilename), nil

}

func updateExtensionImage(metadata *extensionMetadata, content string) string {
	extImage, extImageErr := getDefaultExtensionImage(metadata)
	if extImageErr != nil {
		return content
	}
	searchPattern := fmt.Sprintf(
		`(ghcr\.io\/cloudnative-pg\/%s:)(\d+(?:\.\d+)+)-%d-%s`,
		metadata.ImageName,
		DefaultPgMajor,
		DefaultDistribution,
	)

	re := regexp.MustCompile(searchPattern)

	return re.ReplaceAllString(content, extImage)
}

func updateExtensionVersion(metadata *extensionMetadata, content string) string {
	extVersion, extVersionErr := getDefaultExtensionVersion(metadata)
	if extVersionErr != nil {
		return content
	}

	pattern := fmt.Sprintf(`(- name:\s+%s)(\s+version:\s+)(['"].*?['"])`, regexp.QuoteMeta(metadata.SQLName))
	re := regexp.MustCompile(pattern)

	replacement := fmt.Sprintf(`$1$2'%s'`, extVersion)

	return re.ReplaceAllString(content, replacement)
}
