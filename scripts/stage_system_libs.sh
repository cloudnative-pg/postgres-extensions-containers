#!/usr/bin/env bash
set -eux

# Based on the system-library staging in CloudNativePG's PostGIS image:
# https://github.com/cloudnative-pg/postgres-extensions-containers/blob/main/postgis/Dockerfile

# Get libraries
ldd "$@" | awk '{print $3}' | grep '^/' | sort | uniq > /tmp/all-deps.out
# Extract all the libs that aren't already part of the base image
comm -13 /tmp/base-image-libs.out /tmp/all-deps.out > /tmp/libraries.out

mkdir -p /system /licenses
while read -r lib; do
	resolved=$(readlink -f "$lib")
	dir=$(dirname "$lib")
	base=$(basename "$lib")
	# Copy the real file
	cp -a "$resolved" /system/
	# Reconstruct all its symlinks
	for file in "$dir"/"${base%.so*}.so"*; do
		[ -e "$file" ] || continue
		# If it's a symlink and it resolves to the same real file, we reconstruct it
		if [ -L "$file" ] && [ "$(readlink -f "$file")" = "$resolved" ]; then
			ln -sf "$(basename "$resolved")" "/system/$(basename "$file")"
		fi
	done
done < /tmp/libraries.out

# Preserve aliases supplied as input, such as libmysqlclient.so.
for input_file in "$@"; do
	if [ -L "$input_file" ]; then
		resolved=$(readlink -f "$input_file")
		ln -sf "$(basename "$resolved")" "/system/$(basename "$input_file")"
	fi
done

# Get licenses
for lib in $(find /system -maxdepth 1 -type f -name '*.so*'); do
	# Get the name of the pkg that installed the library
	pkg=$(dpkg -S "$(basename "$lib")" | grep -v "diversion by" | awk -F: '/:/{print $1; exit}')
	[ -z "$pkg" ] && continue
	mkdir -p "/licenses/$pkg" && cp -a "/usr/share/doc/$pkg/copyright" "/licenses/$pkg/copyright"
done
