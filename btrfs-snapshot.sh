#!/bin/sh

set -e

if [ "$#" -ne 3 ]; then
    printf 'Usage: %s <subvolume> <destination> <retain>\n' "$0"
    exit 1
fi

VOLUME_PATH=$(readlink -e "$1")
TO=$(readlink -e "$2")
RETAIN="$3"

if ! btrfs subvolume show "${VOLUME_PATH}" > /dev/null; then
    printf 'not a subvolume: %s\n' "${VOLUME_PATH}"
    exit 1
fi

if [ ! -d "${TO}" ]; then
    printf 'not a directory: %s\n' "${TO}"
    exit 1
fi

case $3 in
    ''|*[!0-9]*)
        printf 'not a number: %s\n' "$3"
        exit 0
        ;;
esac

VOLUME=$(btrfs subvolume show "${VOLUME_PATH}" | grep "Name:" | awk '{print $2}')
btrfs subvolume snapshot -r "${VOLUME_PATH}" "${TO}/${VOLUME}-$(date -u -Iseconds)"

for VOL in $(ls "${TO}" | grep "^${VOLUME}-" | sort | head -n -"${RETAIN}"); do
    btrfs subvolume delete "${TO}/${VOL}"
done
sync
