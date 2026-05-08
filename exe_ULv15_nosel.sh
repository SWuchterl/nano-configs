#!/bin/bash -x

JOBINDEX=${1##*=} # hard coded by crab
NEVENTS=${2##*=}  # ordered by crab.py script
NTHREAD=${3##*=}  # ordered by crab.py script
NAME=${4##*=}     # ordered by crab.py script

WORKDIR=$(pwd)


# 0) get all data files to bypass crab tarball limitations

mkdir -p $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTElectronId/v2/
mkdir -p $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTMuonId/v2

wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTElectronId/v2/electron_ParT_2024.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTElectronId/v2/electron_ParT_2024.onnx
wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTElectronId/v2/preprocess.json -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTElectronId/v2/preprocess.json

wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTMuonId/v2/muon_ParT_2024.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTMuonId/v2/muon_ParT_2024.onnx
wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTMuonId/v2/preprocess.json -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTMuonId/v2/preprocess.json


# 1) run the actual nanoAOD step first
cmsRun -j FrameworkJobReport.xml PSet.py

# outputfile is called nano.root
# rename it
mv nano.root orig_nano.root

# 2) postprocessing with nano_postproc.py

# run the postprocessor with the final selection
nano_postproc.py . orig_nano.root -s _keepdrop --bi $WORKDIR/inputs/keep_and_drop.txt

# now merge the output files into one final nanoAOD file to reduce size
haddnano.py final.root orig_nano_keepdrop.root

# now name the new one nano.root
mv final.root nano.root

# that one should be copied now by crab