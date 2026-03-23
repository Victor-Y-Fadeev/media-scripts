#!/bin/bash


set -e


DIRECTORY="$(realpath "$1")"
FORMAT="postscriptname"
FORMAT="fullname"


while read -r file; do
    EXTENSION="${file##*.}"
    EXTENSION="${EXTENSION,,}"

    FOLDER="$(dirname "${file}")"
    NAME="$(fc-scan --format "%{${FORMAT}}" "${file}")"

    OUTPUT="${FOLDER}/${NAME}.${EXTENSION}"
    TMP="${FOLDER}/TMP.${EXTENSION}"

    mv --force "${file}" "${TMP}"
    mv --force "${TMP}" "${OUTPUT}"
done <<< "$(find "${DIRECTORY}" -maxdepth 1 -type f)"
