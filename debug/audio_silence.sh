#!/bin/bash

COMMON="-y -nostdin -hide_banner -loglevel warning -stats"
INPUT="/mnt/c/Planting Manual/nyaa/AnimeVost/MANUAL"
OUTPUT="/mnt/c/Planting Manual/nyaa/AnimeVost/Silence-Manual"

mkdir --parents "${OUTPUT}"


FRAMES="81"
SAMPLES="$((FRAMES * 1024))"


# === Animevost ===
#
# 03) - 1024 * 2
# 04) - 1024
# 05) - 1024
# 06) - 1024 * 4
# 07) - 1024
# 08) - 1024
# 09) - 1024
# 10) - 1024 * 5
# 11) - 1024
# 12) - 1024
# 13) - 1024
# 14) - 1024




while read -r file; do
    JSON="$(ffprobe -loglevel quiet -select_streams a -show_streams -print_format json "${file}")"
    HZ="$(jq --raw-output '.streams[] | .sample_rate' <<< "${JSON}")"
    CL="$(jq --raw-output '.streams[] | .channel_layout' <<< "${JSON}")"
    CH="$(jq --raw-output '.streams[] | .channels' <<< "${JSON}")"

    echo "${file} ${HZ} ${CL} ${CH}"

    SILENCE="${OUTPUT}/${SAMPLES}-${HZ}-${CL}-${CH}.aac"
    if [[ ! -f "${SILENCE}" ]]; then
        ffmpeg $COMMON -f lavfi -i "anullsrc=r=${HZ}:cl=${CL}" \
            -af "atrim=end_sample=${SAMPLES},asetpts=PTS-STARTPTS,asetnsamples=n=1024:p=1" \
            -ar "${HZ}" -ac "${CH}" -c:a aac -f adts "${SILENCE}"
    fi

    # output="${OUTPUT}/$(basename "${file%.*}")"
    # cp "${SILENCE}" "${output}.silence.aac"

    # DURATION="$(bc --mathlib <<< "(${SAMPLES} + 1024) / ${HZ}")"
    # echo "${file} ${DURATION} ${SAMPLES} ${FRAMES}"

    # ffmpeg $COMMON -i "${file}" -ss "${DURATION}" -map a -c copy -f adts "${output}.cut.aac"
    # cat "${output}.cut.aac" >> "${output}.silence.aac"
    # rm "${output}.cut.aac"
done <<< "$(find "${INPUT}" -maxdepth 1 -type f)"
