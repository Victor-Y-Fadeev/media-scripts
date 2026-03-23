#!/bin/bash

COMMON="-y -nostdin -hide_banner -loglevel warning -stats"
INPUT="/mnt/c/Planting Manual Video/SV-Double"
OUTPUT="/mnt/c/Planting Manual Video/SV-Double-24FPS"
SUFFIX="24FPS"


SCALE="$(bc --mathlib <<< "25 / 24")"
mkdir --parents "${OUTPUT}"


while read -r file; do
    NAME="$(basename "${file}")"
    NAME="${OUTPUT}/${NAME%.*}.${SUFFIX}.ts"
    echo "${NAME}"

    ffmpeg $COMMON -itsscale:v:0 "${SCALE}" -i "${file}" -map v:0 -c copy -f mpegts "${NAME}"
done <<< "$(find "${INPUT}" -maxdepth 1 -type f -name "*.ts")"
