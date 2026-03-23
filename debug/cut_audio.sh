#!/bin/bash

COMMON="-y -nostdin -hide_banner -loglevel warning -stats"

INPUT="/mnt/c/TMP/Slayers/sound"
OUTPUT="/mnt/c/TMP/Slayers/sound"

SUFFIX="CUT_SILENCE"

mkdir --parents "${OUTPUT}"


while read -r file; do
    NAME="$(basename "${file}")"
    NUMBER="${NAME%%.*}"
    ENDING="${NAME#*.}"

    output="${OUTPUT}/${NUMBER}.${SUFFIX}.${ENDING}"

    ORIGINAL="${INPUT}/${NUMBER}. Original.aac"
    FLAC="${INPUT}/${NUMBER}.flac"
    ffmpeg $COMMON -i "${ORIGINAL}" -map a -c flac "${FLAC}"

    JSON="$(ffprobe -loglevel quiet -select_streams a -show_streams -print_format json "${FLAC}")"
    DURATION="$(jq --raw-output '.streams[0].duration' <<< "${JSON}")"
    rm "${FLAC}"

    # SAMPLES="$(bc --mathlib <<< "scale=0; (${DURATION} * 48000 / 1024)")"
    # NEW_DURATION="$(bc --mathlib <<< "scale=3; (${SAMPLES} * 1024) / 48000")"

    # echo "${NUMBER} ${DURATION} ${SAMPLES} ${NEW_DURATION}"

    echo "${ORIGINAL} ${DURATION}"
    # cat "${file}" "${INPUT}/../sls3000.aac" > "${output}"

    # ffmpeg $COMMON -i "${file}" -ss 0.022 -map a -c copy -f adts "${output}"
    ffmpeg $COMMON -i "${file}" -to "${DURATION}" -map a -c copy -f adts "${output}"
    # ffmpeg $COMMON -i "${file}" -ss 0 -to 0 -map a -c copy -f adts "${output}"

done <<< "$(find "${INPUT}" -maxdepth 1 -type f -name "*\&*.aac")"



