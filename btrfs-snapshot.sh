#!/bin/sh

set -e

if [ "$#" -ne 3 ]; then
    printf 'Usage: %s <subvolume> <destination> <retain>\n' "$0"
    exit 1
fi

VOLUME_PATH=$(realpath -e "$1")
TO=$(realpath -e "$2")
RETAIN="$3"

if ! btrfs subvolume show "${VOLUME_PATH}" > /dev/null; then
    printf 'not a subvolume: %s\n' "${VOLUME_PATH}"
    exit 1
fi

if [ ! -d "${TO}" ]; then
    printf 'not a directory: %s\n' "${TO}"
    exit 1
fi

VOLUME=$(btrfs subvolume show "${VOLUME_PATH}" | grep "Name:" | awk '{print $2}')
btrfs subvolume snapshot -r "${VOLUME_PATH}" "${TO}/${VOLUME}-$(date -u -Iseconds)"

PATTERN="[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}+[0-9]\{4\}"
for VOL in $(ls "${TO}" | grep "^${VOLUME}-${PATTERN}\$" | sort | head -n -"${RETAIN}"); do
    btrfs subvolume delete "${TO}/${VOL}"
done
sync
