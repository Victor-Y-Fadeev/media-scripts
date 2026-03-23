#!/usr/bin/env bash
file="$1"

mkvmerge -J "$file" \
  | jq -r '
    .attachments[]
    | select(.content_type | test("(?i)(truetype|opentype|font|ttf|otf)"))
    | "\(.id) \(.file_name)"
  ' \
  | while read -r id name; do
      echo "Extracting attachment $id -> $name"
      mkvextract attachments "$file" "$id:$name"
    done
