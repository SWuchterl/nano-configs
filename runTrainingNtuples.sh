#!/bin/bash
# Submit the lepton ParT training ntuples (mc_2024_NANO.py -> tree.root) with CRAB.
#
# The local data clones PhysicsTools/NanoAOD/data (381 MB) and RecoBTag/Combined/data (417 MB) are larger than the
# 120 MB CRAB sandbox limit (CRAB tars every src/**/data folder). During the submission they are moved to
# $CMSSW_BASE/stash_data. The sandbox then holds only the local-only lepton models that the config loads (ParT v1,
# PNet electron, 21 MB); exe_training.sh downloads the ParT v2 models. All other files come from the release
# (identical to the local clones, checked 2026-10-06). The clones are moved back when the script ends.
#
# usage: ./runTrainingNtuples.sh <sample list> <output LFN dir> <tag> <files per dataset, -1 = all> [--dryrun]
set -e
cd "$(dirname "$0")"
LIST=$1; OUT=$2; TAG=$3; NFILES=$4; DRYRUN=$5
NANO=$CMSSW_BASE/src/PhysicsTools/NanoAOD/data
BTAG=$CMSSW_BASE/src/RecoBTag/Combined/data
STASH=$CMSSW_BASE/stash_data

if [ -e "$STASH" ]; then echo "$STASH exists: move its content back first"; exit 1; fi
mkdir "$STASH"
restore() {
    if [ -d "$STASH/nano" ]; then rm -rf "$NANO"; mv "$STASH/nano" "$NANO"; fi
    if [ -d "$STASH/btag" ]; then mv "$STASH/btag" "$BTAG"; fi
    rmdir "$STASH"
}
trap restore EXIT
mv "$NANO" "$STASH/nano"
mv "$BTAG" "$STASH/btag"
for d in ParTMuonId ParTElectronId PNetElectronId; do
    mkdir -p "$NANO/$d"
    find "$STASH/nano/$d" -maxdepth 1 -type f -exec cp -p {} "$NANO/$d/" \;
done

python3 crab.py -p mc_2024_NANO.py --site T2_CH_CERN -o "$OUT" -t "$TAG" -i "$LIST" -e exe_training.sh \
    --num-cores 2 -s FileBased -n 1 --max-units "$NFILES" --work-area "crab_projects/crab_projects_$TAG" \
    --max-memory 4500 --max-job-runtime 2750 --no-publication $DRYRUN
