#!/bin/bash
# Top-level convenience wrapper: discover input samples then submit condor jobs.
# Runs under the CMSSW_15_0_17 environment python3 (uproot/awkward/pyarrow/numpy).
#
# Usage:
#   ./run_splitter.sh <flavor> <outdir> [options]
#
#   <flavor>   muon | electron
#   <outdir>   output base dir; if it starts with 'root:' parquet is xrdcp'd there
#
# Options (forwarded):
#   --sample GLOB            select samples (repeatable), e.g. --sample 'TTTT*'
#   --files-per-batch N      files merged per condor job   (default 100)
#   --pt-threshold X         pT split boundary             (default 35)
#   --leptons-per-group N    leptons per parquet shard     (default 100000)
#   --submit-test            submit ONE condor job (first batch of first sample)
#   --dry-run                write submit files but do not condor_submit
#   --local-test             run merge on LOCAL .root files, no condor, no xrdcp
#   --local-input PATH       local .root file / dir / .txt filelist for --local-test
#   --local-test-files N     number of local files to use (default 2)
#
# Examples:
#   # local test on 2 local files (no condor, no xrdcp):
#   ./run_splitter.sh muon ./localtest_out --local-test --local-input ../tree.root
#   # single real condor job (first batch of first sample):
#   ./run_splitter.sh muon root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit --sample 'TTTT*' --submit-test
#   # full run:
#   ./run_splitter.sh electron root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit
set -e

if [[ $# -lt 2 ]]; then
    sed -n '2,28p' "$0"
    exit 1
fi

FLAVOR=$1
OUTDIR=$2
shift 2

HERE=$(cd "$(dirname "$0")" && pwd)
# Grid proxy: condor ships it to the worker so its xrdcp can authenticate.
export X509_USER_PROXY="${X509_USER_PROXY:-/tmp/x509up_u$(id -u)}"

# Run under the active CMSSW_15_0_17 environment (provides uproot/awkward/pyarrow/numpy).
PY="$(command -v python3)"
[[ -x "$PY" ]] || { echo "python3 not found; set up the CMSSW_15_0_17 environment first" >&2; exit 1; }
"$PY" -c "import uproot, awkward, pyarrow, numpy" 2>/dev/null || {
    echo "python3 is missing uproot/awkward/pyarrow/numpy; source the CMSSW_15_0_17 environment first" >&2
    exit 1
}

DISCOVER_ARGS=()
SUBMIT_ARGS=()
SAMPLE_ARGS=()
LOCAL_TEST=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sample)            SAMPLE_ARGS+=(--sample "$2"); shift 2 ;;
        --files-per-batch)   DISCOVER_ARGS+=(--files-per-batch "$2"); shift 2 ;;
        --pt-threshold)      SUBMIT_ARGS+=(--pt-threshold "$2"); shift 2 ;;
        --leptons-per-group) SUBMIT_ARGS+=(--leptons-per-group "$2"); shift 2 ;;
        --submit-test)       SUBMIT_ARGS+=(--submit-test); shift ;;
        --dry-run)           SUBMIT_ARGS+=(--dry-run); shift ;;
        --local-test)        SUBMIT_ARGS+=(--local-test); LOCAL_TEST=1; shift ;;
        --local-input)       SUBMIT_ARGS+=(--local-input "$2"); shift 2 ;;
        --local-test-files)  SUBMIT_ARGS+=(--local-test-files "$2"); shift 2 ;;
        *) echo "unknown option: $1" >&2; exit 1 ;;
    esac
done

# Local testing runs on local files only — skip discovery (no xrdfs).
if [[ "$LOCAL_TEST" -eq 0 ]]; then
    echo "=== discover_samples.py ==="
    "$PY" "$HERE/discover_samples.py" "${SAMPLE_ARGS[@]}" "${DISCOVER_ARGS[@]}"
fi

echo "=== submit_condor.py ==="
"$PY" "$HERE/submit_condor.py" \
    --flavor "$FLAVOR" \
    --outdir "$OUTDIR" \
    "${SAMPLE_ARGS[@]}" \
    "${SUBMIT_ARGS[@]}"
