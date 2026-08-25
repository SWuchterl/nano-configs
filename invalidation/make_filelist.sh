#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    echo "Usage: $0 --dataset <dataset> [--date YYMMDD_HHMMSS]"
    exit 1
}

DATASET=""
DATE=""

while [[ $# -gt 0 ]]; do
case "$1" in
--dataset)
            DATASET="$2"
            shift 2
            ;;
--date)
            DATE="$2"
            shift 2
            ;;
        *)
            usage
            ;;
esac
done

if [[ -z "$DATASET" ]]; then
    usage
fi

QUERY="file dataset=${DATASET} instance=prod/phys03"

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

echo "Running DAS query..."
dasgoclient --query "$QUERY" > "$tmpfile"

if [[ -z "$DATE" ]]; then
    # No date given: discover available date folders and take the latest one
    mapfile -t DATES < <(grep -oP '/\K\d{6}_\d{6}(?=/)' "$tmpfile" | sort -u)

    if [[ ${#DATES[@]} -eq 0 ]]; then
        echo "No date folders found for dataset: $DATASET"
        exit 1
    fi

    DATE="${DATES[-1]}"
fi

# Collect files from the requested date folder
mapfile -t FILES < <(grep "/${DATE}/" "$tmpfile")

NFILES=${#FILES[@]}

if [[ $NFILES -eq 0 ]]; then
    echo "No files found for date folder: $DATE"
    exit 1
fi

OUT_DIR="$SCRIPT_DIR/file_lists"
mkdir -p "$OUT_DIR"

FILE_NAMES_OUT="$OUT_DIR/file_list_${DATE}.txt"

echo
echo "Dataset: $DATASET"
echo "Date: $DATE"

printf '%s\n' "${FILES[@]}" > "$FILE_NAMES_OUT"

echo
echo "Found $NFILES files in date folder $DATE."
echo "Created $FILE_NAMES_OUT with all matching files, one per line."