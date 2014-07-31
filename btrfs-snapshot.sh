#!/bin/bash

set -e
TO=$(realpath -e "$1")
NOW=$(date +'%s')
ISO_NOW=$(date +'%Y-%m-%dT%H:%M:%S')
PRUNE_LIMIT=$((60 * 60 * 24))
shift

function prune() {
    VOL="$1"
    LATEST_BACKUP=$(realpath -e "${TO}/${VOL}-latest-backup")
    for S in $(echo "${TO}/${VOL}*"); do
        SNAPSHOT=$(realpath -e ${S})
        if [ ${SNAPSHOT} = ${LATEST_BACKUP} ]; then
            continue
        fi

        TIME=$(date -d$(echo $(basename ${SNAPSHOT}) | cut -d '-' -f 2-) +'%s')
        if [ $((${NOW} - ${TIME})) -ge ${PRUNE_LIMIT} ]; then
            btrfs subvol delete ${SNAPSHOT}
        fi
    done
}

function snapshot() {
    VOL="$1"
    VOL_FULL="$2"
    btrfs subvol snapshot -r "${VOL_FULL}" "${TO}/${VOL}-${ISO_NOW}"
}

for V in "$@"; do
    VOL_FULL=$(realpath -e ${V})
    VOL=$(basename ${VOL_FULL})
    prune ${VOL}
    snapshot ${VOL} ${VOL_FULL}
done
sync
