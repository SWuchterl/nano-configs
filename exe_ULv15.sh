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

# and some more custom models for boosted jets
mkdir -p RecoBTag/Combined/data/HLT/GlobalParticleTransformerAK15/V00/
mkdir -p RecoBTag/Combined/data/InclParticleTransformer-MD/ak15/V02/
mkdir -p RecoBTag/Combined/data/MassRegression/ak15/V01c
mkdir -p RecoBTag/Combined/data/OfflineGlobalParticleTransformerAK15/
mkdir -p RecoBTag/Combined/data/ParticleNet-MD/ak15/V02d

wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/HLT/GlobalParticleTransformerAK15/V00/model_ak15_2024.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/HLT/GlobalParticleTransformerAK15/V00/model_ak15_2024.onnx
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/HLT/GlobalParticleTransformerAK15/V00/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/HLT/GlobalParticleTransformerAK15/V00/preprocess.json
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/InclParticleTransformer-MD/ak15/V02/model.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/InclParticleTransformer-MD/ak15/V02/model.onnx
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/InclParticleTransformer-MD/ak15/V02/preprocess_corr.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/InclParticleTransformer-MD/ak15/V02/preprocess_corr.json
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/MassRegression/ak15/V01c/particle_net_regression.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/MassRegression/ak15/V01c/particle_net_regression.onnx
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/MassRegression/ak15/V01c/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/MassRegression/ak15/V01c/preprocess.json
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/OfflineGlobalParticleTransformerAK15/model_ak15.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/OfflineGlobalParticleTransformerAK15/model_ak15.onnx
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/OfflineGlobalParticleTransformerAK15/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/OfflineGlobalParticleTransformerAK15/preprocess.json
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/ParticleNet-MD/ak15/V02d/particle-net.onnx -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/ParticleNet-MD/ak15/V02d/particle-net.onnx
wget https://github.com/SWuchterl/RecoBTag-Combined-data/raw/refs/heads/dev/CMSSW_15_0_17_nanoV15ExtSkimMore/ParticleNet-MD/ak15/V02d/preprocess.json -O ${CMSSW_BASE}/src/RecoBTag/Combined/data/ParticleNet-MD/ak15/V02d/preprocess.json

# 1) run the actual nanoAOD step first
cmsRun -j FrameworkJobReport.xml PSet.py

# outputfile is called nano.root
# rename it
mv nano.root orig_nano.root

# 2) postprocessing with nano_postproc.py

# create a map with selections for easier handling
# define a map for object cuts
declare -A cut_dict
# original from nanoAOD Run 2
# cut_dict['ele_cut']='Electron_pt>15 && abs(Electron_eta)<2.4 && Electron_mvaIso_WP90 && (abs(Electron_eta+Electron_deltaEtaSC)<1.4442 || abs(Electron_eta+Electron_deltaEtaSC)>1.5560)'
# cut_dict['mu_cut']='Muon_pt>10 && abs(Muon_eta)<2.4 && Muon_tightId && Muon_pfRelIso04_all<0.25'
# cut_dict['tight_ele_cut']='Electron_pt>25 && Electron_mvaIso_WP80'
# cut_dict['tight_mu_cut']='Muon_pt>20 && Muon_pfRelIso04_all<0.15'
# cut_dict['jet_count']='Sum$(Jet_pt>15 && abs(Jet_eta)<2.4)'
# cut_dict['fatjet_count']='Sum$(FatJet_pt>100 && abs(FatJet_eta)<2.5)'

# for now be a bit looser not to throw away interesting events
# later we can tighten again if needed
cut_dict['ele_cut']='Electron_pt>15 && abs(Electron_eta)<2.5'
cut_dict['mu_cut']='Muon_pt>10 && abs(Muon_eta)<2.5'
cut_dict['tight_ele_cut']=${cut_dict[ele_cut]}
cut_dict['tight_mu_cut']=${cut_dict[mu_cut]}
cut_dict['jet_count']='Sum$(Jet_pt>15 && abs(Jet_eta)<2.5)'
cut_dict['fatjet_count']='Sum$(FatJet_pt>100 && abs(FatJet_eta)<2.5)'


# declare a map for base selections
declare -A basesels
basesels['0L']='{jet_count}>=6'
basesels['0L_Wcb']='{jet_count}>=5'
basesels['1L']='(Sum$({ele_cut} && {tight_ele_cut}) + Sum$({mu_cut} && {tight_mu_cut})) >= 1 && {jet_count}>=4'
basesels['1L_Wcb']='(Sum$({ele_cut} && {tight_ele_cut}) + Sum$({mu_cut} && {tight_mu_cut})) >= 1 && {jet_count}>=3'
basesels['2L']='(Sum$({ele_cut}) + Sum$({mu_cut})) >= 2 && (Sum$(Electron_pt>25 && {ele_cut}) + Sum$(Muon_pt>20 && {mu_cut})) >= 1 && {jet_count}>=3'
basesels['0L_TrigSF']='{jet_count}>=6'
basesels['1L_TrigSF']='Sum$({ele_cut})==1 && Sum$(Muon_pt>15 && {mu_cut})==1 && Sum$({ele_cut} && {tight_ele_cut})>=1 && Sum$({mu_cut} && {tight_mu_cut})>=1 && {jet_count}>=4'
basesels['2L_TrigSF']='(Sum$({ele_cut}) + Sum$(Muon_pt>15 && {mu_cut})) == 2 && (Sum$(Electron_pt>25 && {ele_cut}) + Sum$(Muon_pt>25 && {mu_cut})) >= 1'
basesels['1FatJet']='{fatjet_count}>=1'

# now build afinal selection string by combining all base selections with OR
finalsel=""
for sel in "${basesels[@]}"; do
    # replace object cuts in the base selection
    for key in "${!cut_dict[@]}"; do
        sel=${sel//\{$key\}/${cut_dict[$key]}}
    done
    # append to final selection
    if [ -z "$finalsel" ]; then
        finalsel="($sel)"
    else
        finalsel="$finalsel||($sel)"
    fi
done

# print the final selection for debugging
echo "Final selection: $finalsel"

# run the postprocessor with the final selection
nano_postproc.py . orig_nano.root -s _keepdrop --bi $WORKDIR/inputs/keep_and_drop.txt -c "$finalsel"

# now merge the output files into one final nanoAOD file to reduce size
haddnano.py final.root orig_nano_keepdrop.root

# now name the new one nano.root
mv final.root nano.root

# that one should be copied now by crab