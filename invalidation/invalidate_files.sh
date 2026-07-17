#!/usr/bin/env bash
set -uo pipefail

LIST_FILE="files.txt"
DRYRUN=0

usage() {
    echo "Usage: $0 [--input FILE] [--dryrun]"
    echo
    echo "  --input FILE   Path to the list of files (default: files.txt)"
    echo "  --dryrun       Only show how many files would be processed, don't invalidate"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --input)
            [[ -z "${2:-}" ]] && { echo "ERROR: --input requires an argument" >&2; usage; }
            LIST_FILE="$2"
            shift 2
            ;;
        --dryrun)
            DRYRUN=1
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "ERROR: unknown argument: $1" >&2
            usage
            ;;
    esac
done

if [[ ! -f "$LIST_FILE" ]]; then
    echo "ERROR: input file not found: $LIST_FILE" >&2
    exit 1
fi

failed=0
counter=0

while IFS= read -r file; do
    # remove spaces/commas blah blah
    file="$(echo "$file" | sed 's/^[[:space:]"]*//; s/[[:space:]"]*$//')"
    [[ -z "$file" ]] && continue
    ((counter++))

    if (( DRYRUN )); then
        echo "[$counter] Would invalidate:"
        echo "    $file"
        continue
    fi

    echo "[$counter] Invalidating:"
    echo "    $file"
    if ! crab-dev setfilestatus \
        --status INVALID \
        --files "$file"
    then
        echo "ERROR: failed in file $file" >&2
        failed=1
    fi
done < <(tr ',' '\n' < "$LIST_FILE")
# Note: comma-separated lists get split by the tr above; files that are
# already one-per-line (e.g. from file_names.txt) pass through unaffected.

echo
if (( DRYRUN )); then
    echo "Dry run: $counter file(s) would be processed from $LIST_FILE"
    exit 0
fi

echo "Processed files: $counter"
if (( failed != 0 )); then
    echo "At least one failed." >&2
    exit 1
fi
echo "All files set as INVALID"