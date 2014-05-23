#!/bin/bash

set -e
POOL=$(realpath -e "$1")
BACKUP=$(realpath -e "$2")

for VOL in $(ls -1 ${POOL}); do
    NEWEST=${POOL}/.snapshots/$(ls -1 ${POOL}/.snapshots | egrep ${VOL}-[0-9] | tail -1)
    NEWEST_BACKUP=$(realpath -e ${POOL}/.snapshots/${VOL}-latest-backup)

    [ ${NEWEST} = ${NEWEST_BACKUP} ] && echo "${VOL} up to date" && continue

    btrfs send -p ${NEWEST_BACKUP} ${NEWEST} | btrfs receive ${BACKUP}
    ln -sfn ${NEWEST} ${POOL}/.snapshots/${VOL}-latest-backup
done
sync
