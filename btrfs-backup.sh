#!/bin/bash

set -e
POOL=$(realpath -e "$1")
BACKUP=$(realpath -e "$2")

for VOL in $(ls -1 ${POOL}); do
    NEWEST=${POOL}/.snapshots/$(ls -1 ${POOL}/.snapshots | egrep ${VOL} | tail -1)
    NEWEST_BACKUP=${POOL}/.snapshots/$(ls -1 ${BACKUP} | egrep ${VOL} | tail -1)

    [ ${NEWEST} = ${NEWEST_BACKUP} ] && echo "${VOL} up to date" && continue

    if [ -d ${NEWEST_BACKUP} ]
    then
        echo "btrfs send -p ${NEWEST_BACKUP} ${NEWEST} | btrfs receive ${BACKUP}"
    else
        echo "btrfs send ${NEWEST} | btrfs receive ${BACKUP}"
    fi
done
sync
