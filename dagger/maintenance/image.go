package main

import (
	"fmt"
	"regexp"
	"strconv"

	"github.com/google/go-containerregistry/pkg/name"
	"github.com/google/go-containerregistry/pkg/v1/remote"
)

const (
	DefaultPgMajor      = 18
	DefaultDistribution = "trixie"
)

// getImageLabels returns the OCI labels given an image ref.
func getImageLabels(imageRef string) (map[string]string, error) {
	ref, err := name.ParseReference(imageRef)
	if err != nil {
		return nil, err
	}

	desc, err := remote.Get(ref)
	if err != nil {
		return nil, err
	}

	img, err := desc.Image()
	if err != nil {
		return nil, err
	}

	cfg, err := img.ConfigFile()
	if err != nil {
		return nil, err
	}

	return cfg.Config.Labels, nil
}

// getDefaultExtensionImage returns the default extension image for a given extension,
// resolved from the metadata.
func getDefaultExtensionImage(metadata *extensionMetadata) (string, error) {
	packageVersion := metadata.Versions[DefaultDistribution][strconv.Itoa(DefaultPgMajor)]
	re := regexp.MustCompile(`^(\d+(?:\.\d+)+)`)
	matches := re.FindStringSubmatch(packageVersion)
	if len(matches) < 2 {
		return "", fmt.Errorf("cannot extract extension version from %q", packageVersion)
	}
	version := matches[1]
	image := fmt.Sprintf("ghcr.io/cloudnative-pg/%s:%s-%d-%s",
		metadata.ImageName, version, DefaultPgMajor, DefaultDistribution)

	return image, nil
}
