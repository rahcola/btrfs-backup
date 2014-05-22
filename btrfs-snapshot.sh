#!/bin/bash

set -e
TO=$(realpath -e "$1")
shift

for V in "$@"; do
    VOL=$(realpath -e ${V})
    VOLNAME=$(basename ${VOL})
    btrfs subvol snapshot -r ${VOL} ${TO}/${VOLNAME}-$(date +'%Y-%m-%dT%H:%M:%S')
done
sync
