#!/bin/bash -x
# HTCondor executable wrapper for merge_ntuples.py.
#
# Builds a FRESH CMSSW_15_0_17 release on the worker node (provides python3 +
# uproot/awkward/numpy and xrdcp), then runs the merge script. merge_ntuples.py
# and the batch filelist are transferred by condor into $_CONDOR_SCRATCH_DIR.
#
# Positional args (set by submit_condor.py queue file):
#   1 flavor  2 sample  3 tag  4 batch_id  5 filelist(basename)
#   6 outdir  7 pt_threshold  8 leptons_per_group
set -e

FLAVOR=$1
SAMPLE=$2
TAG=$3
BATCH_ID=$4
FILELIST=$5
OUTDIR=$6
PT_THRESHOLD=$7
LEPTONS_PER_GROUP=$8

WORKDIR=${_CONDOR_SCRATCH_DIR:-$(pwd)}
cd "$WORKDIR"

# --- fresh CMSSW_15_0_17 environment on the worker ---
shopt -s expand_aliases                      # so cmsrel/cmsenv aliases expand in the script
export SCRAM_ARCH=el9_amd64_gcc12
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch      # worker may not have this set
source "$VO_CMS_SW_DIR/cmsset_default.sh"
cmsrel CMSSW_15_0_17                          # == scram project CMSSW CMSSW_15_0_17
cd CMSSW_15_0_17/src
cmsenv                                        # == eval `scramv1 runtime -sh`
cd "$WORKDIR"

# stage xrdcp copies / parquet output in the job scratch dir
export TMPDIR="$WORKDIR"

python3 merge_ntuples.py \
    --flavor "$FLAVOR" \
    --filelist "$FILELIST" \
    --sample "$SAMPLE" \
    --tag "$TAG" \
    --outdir "$OUTDIR" \
    --pt-threshold "$PT_THRESHOLD" \
    --leptons-per-group "$LEPTONS_PER_GROUP" \
    --batch-id "$BATCH_ID" \
    --tmpdir "$TMPDIR"

exit $?
