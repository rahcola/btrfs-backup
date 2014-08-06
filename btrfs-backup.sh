#!/bin/bash

set -e
POOL=$(realpath -e "$1")
BACKUP=$(realpath -e "$2")

for L in $(ls -1 ${POOL} | grep "latest-backup$"); do
    LATEST_BACKUP=$(realpath -e ${POOL}/${L})
    VOL=$(basename ${LATEST_BACKUP} | cut -d '-' -f 1)
    LATEST=$(realpath -e ${POOL}/$(ls -1 ${POOL} | grep ${VOL} | grep -v "latest-backup$" | sort | tail -1))

    [ ${LATEST} = ${LATEST_BACKUP} ] && echo "${VOL} up to date" && continue

    btrfs send -p ${LATEST_BACKUP} ${LATEST} | btrfs receive ${BACKUP}
    sync
    ln -sfn ${LATEST} ${POOL}/${VOL}-latest-backup
done
