#!/bin/bash

set -e
D=$(realpath -e "$1")
NOW=$(date +'%s')

for V in $(ls -1 ${D}); do
    VOL=$(basename ${V})
    TIME=$(date -d$(echo ${VOL} | cut -d '-' -f 2-) +'%s')
    DELTA=$((${NOW} - ${TIME}))
    if [ ${DELTA} -ge 86400 ]
    then
        btrfs subvol delete ${D}/${VOL}
    fi
done
