#!/bin/bash

set -e
SPATH=$(realpath -e "$1")
NOW=$(date +'%s')

for V in $(ls -1 ${SPATH}); do
    SNAPSHOT=$(realpath -e ${SPATH}/${V})
    VOL=$(echo ${V} | cut -d '-' -f 1)
    LATEST_BACKUP=$(realpath -e ${SPATH}/${VOL}-latest-backup)
    [ ${SNAPSHOT} = ${LATEST_BACKUP} ] && continue

    TIME=$(date -d$(echo ${V} | cut -d '-' -f 2-) +'%s')
    DELTA=$((${NOW} - ${TIME}))
    if [ ${DELTA} -ge 86400 ]
    then
        btrfs subvol delete ${SNAPSHOT}
    fi
done
sync
