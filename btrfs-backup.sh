#!/bin/sh

set -e

if [ "$#" -ne 2 ]; then
    printf "Usage: %s <source> <destination>\n" "$0"
    exit 1
fi

FROM=$(realpath -e "$1")
TO="$2"

if [ ! -d "${FROM}" ]; then
    printf "not a directory: %s\n" "${FROM}"
    exit 1
fi

LATEST=$(ls ${FROM} | grep -v "^synced-" | sort | tail -n 1)
SYNCED=$(ls ${FROM} | grep "^synced-" | sort | tail -n 1)

if [ -z "${LATEST}" ]; then
    printf "nothing to backup\n"
    exit 0
fi

if [ "${SYNCED}" = "synced-${LATEST}" ]; then
    printf "up to date\n"
    exit 0
fi

if [ -d "${TO}" ]; then
    TO=$(realpath -e "${TO}")
    btrfs subvolume snapshot -r "${FROM}/${LATEST}" "${FROM}/sync-${LATEST}"
    if [ -z "${SYNCED}" ]; then
        btrfs send "${FROM}/sync-${LATEST}" \
            | btrfs receive "${TO}"
        sync
    else
        btrfs send -p "${FROM}/${SYNCED}" "${FROM}/sync-${LATEST}" \
            | btrfs receive "${TO}"
        sync
        btrfs subvolume delete "${FROM}/${SYNCED}"
    fi
    mv "${FROM}/sync-${LATEST}" "${FROM}/synced-${LATEST}"
    mv "${TO}/sync-${LATEST}" "${TO}/${LATEST}"
else
    printf "not a valid destination: %s\n" "${TO}"
    exit 1
fi
