package main

import (
	"bytes"
	"fmt"
	"regexp"
	"strconv"

	"github.com/google/go-containerregistry/pkg/name"
	containerregistryv1 "github.com/google/go-containerregistry/pkg/v1"
	"github.com/google/go-containerregistry/pkg/v1/remote"
	ocispecv1 "github.com/opencontainers/image-spec/specs-go/v1"
)

const (
	DefaultPgMajor      = 18
	DefaultDistribution = "trixie"
)

// getImageAnnotations returns the OCI annotations given an image ref.
func getImageAnnotations(imageRef string) (map[string]string, error) {
	ref, err := name.ParseReference(imageRef)
	if err != nil {
		return nil, err
	}

	head, err := remote.Get(ref)
	if err != nil {
		return nil, err
	}

	switch head.MediaType {
	case ocispecv1.MediaTypeImageIndex:
		indexManifest, err := containerregistryv1.ParseIndexManifest(bytes.NewReader(head.Manifest))
		if err != nil {
			return nil, err
		}
		return indexManifest.Annotations, nil
	case ocispecv1.MediaTypeImageManifest:
		manifest, err := containerregistryv1.ParseManifest(bytes.NewReader(head.Manifest))
		if err != nil {
			return nil, err
		}
		return manifest.Annotations, nil
	}

	return nil, fmt.Errorf("unsupported media type: %s", head.MediaType)
}

// getDefaultExtensionImage returns the default extension image for a given extension,
// resolved from the metadata.
func getDefaultExtensionImage(metadata *extensionMetadata) (string, error) {
	version, err := getDefaultExtensionVersion(metadata)
	if err != nil {
		return "", err
	}
	image := fmt.Sprintf("ghcr.io/cloudnative-pg/%s:%s-%d-%s",
		metadata.ImageName, version, DefaultPgMajor, DefaultDistribution)

	return image, nil
}

// getDefaultExtensionVersion returns the default extension version for a given extension,
// resolved from the metadata.
func getDefaultExtensionVersion(metadata *extensionMetadata) (string, error) {
	packageVersion := metadata.Versions[DefaultDistribution][strconv.Itoa(DefaultPgMajor)]
	if packageVersion == "" {
		return "", fmt.Errorf("no package version found for distribution %q and version %d",
			DefaultDistribution, DefaultPgMajor)
	}

	re := regexp.MustCompile(`^(\d+(?:\.\d+)+)`)
	matches := re.FindStringSubmatch(packageVersion)
	if len(matches) < 2 {
		return "", fmt.Errorf("cannot extract extension version from %q", packageVersion)
	}
	version := matches[1]
	return version, nil
}
