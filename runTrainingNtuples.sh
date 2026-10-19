#!/bin/bash
# Submit the 2024 lepton ParT training ntuples (mc_2024_NANO.py -> tree.root) with CRAB, stage-out at T2B.
#
# Three sample sets, each its own CRAB work area, all written to $OUT:
#   general   mc/training_ntuples/mc_2024.conf           electron + muon trees (leptons=both)
#   electron  mc/training_ntuples/mc_2024_electron.conf  electron tree only     (leptons=electron)
#   muon      mc/training_ntuples/mc_2024_muon.conf      muon tree only         (leptons=muon)
#
# The local data clones PhysicsTools/NanoAOD/data (381 MB) and RecoBTag/Combined/data (417 MB) are larger than the
# 120 MB CRAB sandbox limit (CRAB tars every src/**/data folder). During the submission they are moved to
# $CMSSW_BASE/stash_data. The sandbox then holds only the local-only lepton models that the config loads (ParT v1,
# PNet electron, 21 MB); exe_training.sh downloads the ParT v2 models. All other files come from the release
# (identical to the local clones, checked 2026-10-06). The clones are moved back when the script ends.
#
# usage: ./runTrainingNtuples.sh [general] [electron] [muon] [--dryrun]   (no set given: all three)
set -e
cd "$(dirname "$0")"

# ---- production settings ----
OUT=/store/user/juvanden/CMSSW_15_0_17_ntuples_v2/2024
SITE=T2_BE_IIHE
VERSION=v2
declare -A LIST=([general]=mc/training_ntuples/mc_2024.conf
                 [electron]=mc/training_ntuples/mc_2024_electron.conf
                 [muon]=mc/training_ntuples/mc_2024_muon.conf)
declare -A LEPTONS=([general]=both [electron]=electron [muon]=muon)
# MiniAOD files per job (FileBased), all files of each dataset are processed.
# Local timing 2026-10-19 (2 threads; TTtoLNu2Q 0.082 s/event, WtoLNu ~0.055, DYto2Tau 0.027; electron-only 0.85x,
# muon-only 0.53x; peak RSS 3.4 GB): slowest job ~10 h general, ~8 h electron, ~9 h muon on this node.
declare -A FILES_PER_JOB=([general]=10 [electron]=10 [muon]=20)
# -----------------------------

SETS=()
DRYRUN=""
for arg in "$@"; do
    case "$arg" in
        --dryrun) DRYRUN="--dryrun" ;;
        general|electron|muon) SETS+=("$arg") ;;
        *) echo "unknown argument: $arg"; exit 1 ;;
    esac
done
[ ${#SETS[@]} -eq 0 ] && SETS=(general electron muon)

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

for s in "${SETS[@]}"; do
    TAG=LeptonParT-$VERSION-$s
    echo "=== $s: ${LIST[$s]}, leptons=${LEPTONS[$s]}, ${FILES_PER_JOB[$s]} files per job, tag $TAG"
    python3 crab.py -p mc_2024_NANO.py --site $SITE -o "$OUT" -t "$TAG" -i "${LIST[$s]}" -e exe_training.sh \
        --pycfg-params leptons=${LEPTONS[$s]} \
        --num-cores 2 -s FileBased -n ${FILES_PER_JOB[$s]} --max-units -1 --work-area "crab_projects/crab_projects_$TAG" \
        --max-memory 4500 --max-job-runtime 2750 --no-publication $DRYRUN
done
