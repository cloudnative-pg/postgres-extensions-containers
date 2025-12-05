package main

import (
	"context"
	"fmt"
	"path"
	"regexp"

	"dagger/maintenance/internal/dagger"
)

// libsRegex matches library dependencies from apt-get output
// Format: library-name MD5Sum:checksum
var libsRegex = regexp.MustCompile(`(?m)^.*\s(lib\S*).*(MD5Sum:.*)$`)

func updateOSLibsOnTarget(
	ctx context.Context,
	target string,
	distribution string,
	majorVersion string,
) (*dagger.File, error) {
	postgresBaseImage := fmt.Sprintf("ghcr.io/cloudnative-pg/postgresql:%s-minimal-%s", majorVersion, distribution)
	packageName := fmt.Sprintf("postgresql-%s-%s", majorVersion, target)

	out, err := dag.Container().
		From(postgresBaseImage).
		WithUser("root").
		WithExec([]string{"apt-get", "update"}).
		WithExec([]string{"bash",
			"-c",
			"apt-get install -qq --print-uris --no-install-recommends " + packageName,
		}).Stdout(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch OS libs for extension %s (PostgreSQL %s on %s): %w",
			target, majorVersion, distribution, err)
	}

	matches := libsRegex.FindAllStringSubmatch(out, -1)
	if len(matches) == 0 {
		return nil, fmt.Errorf("no library dependencies found for extension %s (PostgreSQL %s on %s): apt-get may have failed or package has no lib dependencies",
			target, majorVersion, distribution)
	}

	var result string
	for _, m := range matches {
		if len(m) >= 3 {
			result += m[1] + " " + m[2] + "\n"
		}
	}

	if result == "" {
		return nil, fmt.Errorf("parsed empty content for extension %s (PostgreSQL %s on %s): regex matched but extracted no data",
			target, majorVersion, distribution)
	}

	fileName := fmt.Sprintf("%s-%s-os-libs.txt", majorVersion, distribution)
	file := dag.File(fileName, result)

	return file, nil
}

func extensionsWithOSLibs(
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
		if metadata.AutoUpdateOsLibs {
			dirName, err := dir.Name(ctx)
			if err != nil {
				return nil, err
			}
			extensions[path.Dir(dirName)] = metadata.Name
		}
	}

	return extensions, nil
}

func extensionsDirectories(ctx context.Context, source *dagger.Directory) ([]*dagger.Directory, error) {
	paths, err := source.Glob(ctx, path.Join("**", metadataFile))
	if err != nil {
		return nil, err
	}
	directories := make([]*dagger.Directory, 0, len(paths))
	for _, p := range paths {
		directories = append(directories, source.Directory(path.Dir(p)))
	}

	return directories, nil
}
