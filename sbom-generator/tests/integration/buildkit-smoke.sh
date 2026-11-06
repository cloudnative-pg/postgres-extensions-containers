#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 GENERATOR_IMAGE OUTPUT_DIRECTORY [FIXTURE_TAG]" >&2
  exit 2
fi

generator_image=$1
artifact_dir=$(mkdir -p "$2" && cd "$2" && pwd)
fixture_tag=${3:-"manual-$(date -u +%Y%m%d%H%M%S)-$$"}
registry=${SBOM_SMOKE_REGISTRY:-localhost:5000}
grant_image=${GRANT_IMAGE:?GRANT_IMAGE must name a pinned Grant image}
grype_image=${GRYPE_IMAGE:?GRYPE_IMAGE must name a pinned Grype image}
python=${PYTHON:-python3}
builder=${BUILDX_BUILDER:-}
platform=${SBOM_SMOKE_PLATFORM:-linux/amd64}
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$script_dir/../../.." && pwd)
fixture_context="$script_dir/fixture"
fixture_image="$registry/cnpg-sbom-smoke:$fixture_tag"

for command in docker "$python"; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "required command is unavailable: $command" >&2
    exit 1
  fi
done
docker buildx version >/dev/null

build_args=(buildx build --platform "$platform" --tag "$fixture_image"
  --attest "type=sbom,generator=$generator_image"
  --metadata-file "$artifact_dir/build-metadata.json"
  --push)
if [[ -n "$builder" ]]; then
  build_args+=(--builder "$builder")
fi
build_args+=("$fixture_context")
docker "${build_args[@]}"

# Buildx exposes the SBOM attached to the pushed fixture image as platform
# metadata. The fixture itself is pushed only to the disposable local registry.
docker buildx imagetools inspect "$fixture_image" \
  --format '{{ json .SBOM.SPDX }}' \
  > "$artifact_dir/fixture.spdx.json"
if [[ ! -s "$artifact_dir/fixture.spdx.json" ]]; then
  echo "BuildKit did not export an SPDX predicate for $fixture_image" >&2
  exit 1
fi

docker run --rm --platform "$platform" --entrypoint python3 \
  --volume "$artifact_dir:/results:ro" \
  "$generator_image" /opt/cnpg-sbom-generator/spdx_validation.py \
  /results/fixture.spdx.json

docker run --rm --user "$(id -u):$(id -g)" \
  --volume "$artifact_dir:/results" "$grant_image" \
  list /results/fixture.spdx.json -o json > "$artifact_dir/grant.json"

docker run --rm --env GRYPE_DB_CACHE_DIR=/tmp/grype-db \
  --volume "$artifact_dir:/results" "$grype_image" \
  sbom:/results/fixture.spdx.json -o json > "$artifact_dir/grype.json"

"$python" "$script_dir/check_buildkit_smoke.py" \
  "$artifact_dir/fixture.spdx.json" "$artifact_dir/grant.json" "$artifact_dir/grype.json"

echo "Fixture image: $fixture_image"
echo "Artifacts: $artifact_dir"
