package main

import (
	"bytes"
	"fmt"
	"regexp"
	"strconv"

	"github.com/google/go-containerregistry/pkg/crane"
	"github.com/google/go-containerregistry/pkg/name"
	containerregistryv1 "github.com/google/go-containerregistry/pkg/v1"
	"github.com/google/go-containerregistry/pkg/v1/remote"
	ocispecv1 "github.com/opencontainers/image-spec/specs-go/v1"
)

const (
	DefaultPgMajor      = 18
	DefaultDistribution = "trixie"
)

var SupportedDistributions = []string{
	"bookworm",
	"trixie",
}

// getImageAnnotations returns the OCI annotations given an image ref.
func getImageAnnotations(imageRef string) (map[string]string, error) {
	// Setting Insecure option to allow fetching images from local registries with no TLS
	ref, err := name.ParseReference(imageRef, name.Insecure)
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
	return getExtensionImage(metadata, DefaultDistribution, DefaultPgMajor)
}

// getExtensionImage returns the extension image for a given distribution and pgMajor.
func getExtensionImage(metadata *extensionMetadata, distribution string, pgMajor int) (string, error) {
	version, err := extractExtensionVersion(metadata.Versions, distribution, pgMajor)
	if err != nil {
		return "", fmt.Errorf("while extracting extension version for %s: %w", metadata.Name, err)
	}

	image := fmt.Sprintf("ghcr.io/cloudnative-pg/%s:%s-%d-%s",
		metadata.ImageName, version, pgMajor, distribution)

	return image, nil
}

// getExtensionImageWithTimestamp returns the extension image with the latest timestamp
// for a given distribution and pgMajor.
func getExtensionImageWithTimestamp(metadata *extensionMetadata, distribution string, pgMajor int) (string, error) {
	imageName := fmt.Sprintf("ghcr.io/cloudnative-pg/%s", metadata.ImageName)
	tags, err := crane.ListTags(imageName)
	if err != nil {
		return "", fmt.Errorf("while listing tags for image %s: %w", imageName, err)
	}

	version, err := extractExtensionVersion(metadata.Versions, distribution, pgMajor)
	if err != nil {
		return "", fmt.Errorf("while extracting extension version for %s: %w", metadata.Name, err)
	}

	re := regexp.MustCompile(
		fmt.Sprintf(`^%s-(\d{12})-%d-%s$`,
			regexp.QuoteMeta(version),
			pgMajor,
			distribution,
		),
	)

	var latestTag string
	for _, tag := range tags {
		if re.MatchString(tag) && tag > latestTag {
			latestTag = tag
		}
	}
	if latestTag == "" {
		return "", fmt.Errorf(
			"no image found for image %s (version=%s pgMajor=%d os=%s)",
			imageName, version, pgMajor, distribution,
		)
	}

	imageRef := fmt.Sprintf("%s:%s", imageName, latestTag)

	ref, err := name.ParseReference(imageRef, name.Insecure)
	if err != nil {
		return "", fmt.Errorf("while parsing image reference %s: %w", imageRef, err)
	}

	desc, err := remote.Get(ref)
	if err != nil {
		return "", fmt.Errorf("while fetching digest for image %s: %w", imageRef, err)
	}

	return fmt.Sprintf("%s@%s", imageRef, desc.Digest.String()), nil
}

// extractExtensionVersion returns the extension version for a given distribution and pgMajor,
// extracted from the extension's metadata.
func extractExtensionVersion(versions versionMap, distribution string, pgMajor int) (string, error) {
	packageVersion := versions[distribution][strconv.Itoa(pgMajor)]
	if packageVersion == "" {
		return "", fmt.Errorf("no package version found for distribution %q and version %d",
			distribution, pgMajor)
	}

	re := regexp.MustCompile(`^(\d+(?:\.\d+)+)`)
	matches := re.FindStringSubmatch(packageVersion)
	if len(matches) < 2 {
		return "", fmt.Errorf("cannot extract extension version from %q", packageVersion)
	}

	return matches[1], nil
}
