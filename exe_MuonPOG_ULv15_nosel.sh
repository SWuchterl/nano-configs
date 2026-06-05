#!/bin/bash -x

JOBINDEX=${1##*=} # hard coded by crab
NEVENTS=${2##*=}  # ordered by crab.py script
NTHREAD=${3##*=}  # ordered by crab.py script
NAME=${4##*=}     # ordered by crab.py script

WORKDIR=$(pwd)


# 0) get all data files to bypass crab tarball limitations

# 0) get all data files to bypass crab tarball limitations

mkdir -p $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTElectronId/v2/
mkdir -p $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTMuonId/v2

wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTElectronId/v2/electron_ParT_2024.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTElectronId/v2/electron_ParT_2024.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTElectronId/v2/preprocess.json -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTElectronId/v2/preprocess.json --tries=0 --retry-connrefused --wait=30

wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTMuonId/v2/muon_ParT_2024.onnx -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTMuonId/v2/muon_ParT_2024.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTMuonId/v2/preprocess.json -O $CMSSW_BASE/src/PhysicsTools/NanoAOD/data/ParTMuonId/v2/preprocess.json --tries=0 --retry-connrefused --wait=30

# and some more custom models for boosted jets
mkdir -p ${CMSSW_BASE}/src/RecoBTag/Combined/data/HLT/GlobalParticleTransformerAK15/V00/
mkdir -p ${CMSSW_BASE}/src/RecoBTag/Combined/data/InclParticleTransformer-MD/ak15/V02/
mkdir -p ${CMSSW_BASE}/src/RecoBTag/Combined/data/MassRegression/ak15/V01c
mkdir -p ${CMSSW_BASE}/src/RecoBTag/Combined/data/OfflineGlobalParticleTransformerAK15/
mkdir -p ${CMSSW_BASE}/src/RecoBTag/Combined/data/ParticleNet-MD/ak15/V02d

wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/HLT/GlobalParticleTransformerAK15/V00/model_ak15_2024.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/HLT/GlobalParticleTransformerAK15/V00/model_ak15_2024.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/HLT/GlobalParticleTransformerAK15/V00/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/HLT/GlobalParticleTransformerAK15/V00/preprocess.json --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/InclParticleTransformer-MD/ak15/V02/model.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/InclParticleTransformer-MD/ak15/V02/model.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/InclParticleTransformer-MD/ak15/V02/preprocess_corr.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/InclParticleTransformer-MD/ak15/V02/preprocess_corr.json --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/MassRegression/ak15/V01c/particle_net_regression.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/MassRegression/ak15/V01c/particle_net_regression.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/MassRegression/ak15/V01c/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/MassRegression/ak15/V01c/preprocess.json --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/OfflineGlobalParticleTransformerAK15/model_ak15.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/OfflineGlobalParticleTransformerAK15/model_ak15.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/OfflineGlobalParticleTransformerAK15/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/OfflineGlobalParticleTransformerAK15/preprocess.json --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/ParticleNet-MD/ak15/V02d/particle-net.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/ParticleNet-MD/ak15/V02d/particle-net.onnx --tries=0 --retry-connrefused --wait=30
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/ParticleNet-MD/ak15/V02d/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/ParticleNet-MD/ak15/V02d/preprocess.json --tries=0 --retry-connrefused --wait=30

# 1) run the actual nanoAOD step first
cmsRun -j FrameworkJobReport.xml PSet.py

# outputfile is called nano.root
# rename it
mv nano.root orig_nano.root

# 2) postprocessing with nano_postproc.py

# run the postprocessor with the final selection
# nano_postproc.py . orig_nano.root -s _keepdrop --bi $WORKDIR/inputs/keep_and_drop.txt

# now merge the output files into one final nanoAOD file to reduce size
haddnano.py final.root orig_nano.root

# now name the new one nano.root
mv final.root nano.root

# that one should be copied now by crab