#!/bin/bash -x
# CRAB job for the lepton ParT training ntuples: the config writes tree.root (TFileService), no nano.root

# lepton ParT models, downloaded because of the CRAB sandbox size limit
for f in ParTElectronId/v2/electron_ParT_2024.onnx ParTElectronId/v2/preprocess.json \
         ParTMuonId/v2/muon_ParT_2024.onnx ParTMuonId/v2/preprocess.json; do
    mkdir -p $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/$(dirname $f)
    wget -nv https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/$f \
        -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/$f --tries=0 --retry-connrefused --wait=30
done

cmsRun -j FrameworkJobReport.xml PSet.py
