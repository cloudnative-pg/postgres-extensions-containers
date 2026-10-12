#!/usr/bin/env bash
set -euxo pipefail

# Run before installing extension packages so staging can exclude libraries
# already supplied by the base image.
if ! ldconfig -p | awk '{print $NF}' | grep '^/' | sort | uniq > /tmp/base-image-libs.out; then
	rm -f /tmp/base-image-libs.out
	echo "ERROR: Could not capture base image libraries with ldconfig -p." >&2
	exit 1
fi

if [ ! -s /tmp/base-image-libs.out ]; then
	echo "ERROR: No base image libraries detected by ldconfig -p." >&2
	exit 1
fi
