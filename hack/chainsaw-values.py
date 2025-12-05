#
# Copyright © contributors to CloudNativePG, established as
# CloudNativePG a Series of LF Projects, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
#

import argparse
import re
import sys
import hcl2
import yaml
from pathlib import Path


def parse_hcl(metadata_path):
    with open(metadata_path, "r") as f:
        return hcl2.load(f)["metadata"]


def get_default_image(metadata, distro, pg_major):
    fullVersion = metadata["versions"][distro][pg_major]
    match = re.match(r"^(\d+(?:\.\d+)+)", fullVersion)
    if not match:
        raise ValueError(f"Cannot extract extension version from '{s}'")
    version = match.group(1)
    image_name = metadata["image_name"]
    return f"ghcr.io/cloudnativepg/{image_name}:{version}-{pg_major}-{distro}"


def get_ext_version(ext_image):
    tag = ext_image.split(":", 1)[1]
    version = tag.split("-", 1)[0]
    return version


def main():
    parser = argparse.ArgumentParser(
        description="Generate Chainsaw values.yaml for a target Extension"
    )
    parser.add_argument(
        "--dir", type=Path, required=True, help="Path to the extension's directory"
    )
    parser.add_argument(
        "--pg-major",
        choices=["18"],
        required=True,
        dest="pg_major",
        help="The PG major version to test",
    )
    parser.add_argument(
        "--distro",
        choices=["bookworm", "trixie"],
        required=True,
        help="The distribution to test",
    )
    parser.add_argument(
        "--extension-image",
        dest="ext_image",
        help="Target a specific extension image (Optional). Defaults to the version defined in the extension's metadata",
    )
    args = parser.parse_args()

    ext_dir = Path(args.dir)
    metadata_file = ext_dir / "metadata.hcl"
    if not metadata_file.exists():
        print(f"Error: {metadata_file} does not exist")
        sys.exit(1)

    metadata = parse_hcl(metadata_file)

    ext_image = args.ext_image or get_default_image(
        metadata, args.distro, args.pg_major
    )
    version = get_ext_version(ext_image)
    pg_image = (
        f"ghcr.io/cloudnative-pg/postgresql:{args.pg_major}-minimal-{args.distro}"
    )

    # Build the values.yaml dictionary
    values = {
        **metadata,
        "extension_image": ext_image,
        "pg_image": pg_image,
        "version": version,
    }

    # Write values.yaml
    values_yaml_path = ext_dir / "values.yaml"
    with open(values_yaml_path, "w") as f:
        yaml.dump(values, f, sort_keys=False)

    print(f"Generated {values_yaml_path}")


if __name__ == "__main__":
    main()
