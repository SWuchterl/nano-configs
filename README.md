# nano-configs

Produce NanoAODs with customizations.

<!-- TOC -->

- [nano-configs](#nano-configs)
    - [Version](#version)
    - [Setup](#setup)
    - [Production](#production)

<!-- /TOC -->

---

## Version

The current version is based on the Run2UL config in `CMSSW_15_0_15_patch4`, but we use `CMSSW_15_0_17`, so it is based on [NanoAODv15](https://gitlab.cern.ch/cms-nanoAOD/nanoaod-doc/-/wikis/Releases/NanoAODv15).

Customizations:
- Add custom PNet and two ParT output scores for electrons and muons.
- Add our custom ParT output scores for AK4 Puppi jets w/o PID inputs.
- Store all PS weights.
- Store topPt weights for 13 and 13.6 TeV.
- Store b and c fragmentation and b and c hadron decay BR weights.
- Store TOP ML systematics weights, see [here](https://twiki.cern.ch/twiki/bin/view/CMS/MLReweighting).
- Store sumW for renormalization weights for each tt+(cc/cj/2c/bb/bj/2b/lf) subprocess.
- Skim nanoAOD "heavily" using NANOAOD PostProcessing tools.

---

## Setup

Use EL8 or singularity container `cmssw-el8`!

```bash
export SCRAM_ARCH=el8_amd64_gcc12
cmsrel CMSSW_15_0_17
cd CMSSW_15_0_17/src
cmsenv

git cms-init

# For AK4Puppi ParT w/o PID, lepton PNET and ParT, and TOP weight modifications
git cms-addpkg DataFormats/BTauReco
git cms-addpkg PhysicsTools/PatAlgos
git cms-addpkg PhysicsTools/NanoAOD
git cms-addpkg PhysicsTools/NanoAODTools
git cms-addpkg RecoBTag/Combined
git cms-addpkg RecoBTag/Configuration
git cms-addpkg RecoBTag/FeatureTools
git cms-addpkg RecoBTag/ONNXRuntime

# get the necessary modules from the TOP PAG, modified:
mkdir TopQuarkAnalysis
cd TopQuarkAnalysis
git clone https://gitlab.cern.ch/tthcc-run-3/BFragmentationAnalyzer.git -b dev/CMSSW_15_0_17_nanoV15ExtSkim
cd ..

# now the modified release for TOP weights and AK4Puppi ParT
git cms-merge-topic -u SWuchterl:dev/CMSSW_15_0_17_nanoV15ExtSkimLeptonParT

# and for the leptons (not needed anymore)
# git cms-merge-topic -u JulesVandenbroeck:dev/CMSSW_15_0_17_leptonParT

# get the jet ParT data files
git clone git@github.com:SWuchterl/RecoBTag-Combined-data.git -b dev/CMSSW_15_0_17_nanoV15ExtSkim RecoBTag/Combined/data/

# get the lepton PNET and ParT data files (nearly all)
git clone -b CMSSW_15_0_2_patchX_leptonParT git@github.com:JulesVandenbroeck/PhysicsTools-NanoAOD.git PhysicsTools/NanoAOD/data

# we need for local tests to add the following files/folders, but it would increase the tarball for CRAB too much (>120 MB), so when submitting needs to be deleted. It will be handled by out shell excutable.
mkdir -p PhysicsTools/NanoAOD/data/ParTElectronId/v2/
mkdir -p PhysicsTools/NanoAOD/data/ParTMuonId/v2

wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTElectronId/v2/electron_ParT_2024.onnx PhysicsTools/NanoAOD/data/ParTElectronId/v2/
wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTElectronId/v2/preprocess.json PhysicsTools/NanoAOD/data/ParTElectronId/v2/

wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTMuonId/v2/muon_ParT_2024.onnx PhysicsTools/NanoAOD/data/ParTMuonId/v2/
wget https://github.com/SWuchterl/PhysicsTools-NanoAOD/raw/refs/heads/CMSSW_15_0_17_leptonParT/ParTMuonId/v2/preprocess.json PhysicsTools/NanoAOD/data/ParTMuonId/v2/

# and compile
scram b -j8
cmsenv
```

## Production

**Step 0**: switch to the crab production directory and set up grid proxy, CRAB environment, etc.

```bash
# set up grid proxy
voms-proxy-init -rfc -voms cms --valid 168:00
# set up CRAB env (must be done after cmsenv)
source /cvmfs/cms.cern.ch/common/crab-setup.sh
```

**Step 1**: clone the repo and generate the python config file with `generateConfigs.sh`:

```bash
git clone https://github.com/SWuchterl/nano-configs.git -b dev/CMSSW_15_0_17_nanoV15ExtSkim
cd nano-configs
./generateConfigs.sh
```

**Step 2**: use the `crab.py` script to submit the CRAB jobs:

For MC:

- 2018:

```bash
python3 crab.py -p mc_2018UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2018/mc -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i mc/mc_2018.conf --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2018ULv15 --input-files inputs --max-memory 3000 --no-publication --dryrun
```

- 2017:

```bash
./crab.py -p mc_2017UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2017/mc -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i mc/mc_2017.conf -e exe_ULv15.sh -s FileBased -n 2 --num-cores 1 --work-area crab_projects_2017ULv15 --input-files inputs --max-memory 3000 --no-publication --dryrun
```

- 2016postVFP:

```bash
python3 crab.py -p mc_2016ULpostVFP_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2016/mc -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i mc/mc_2016post.conf --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2016ULpostVFPv15 --input-files inputs --max-memory 3000 --no-publication --dryrun
```

- 2016preVFP:

```bash
python3 crab.py -p mc_2016ULpreVFP_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2016APV/mc -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i mc/mc_2016pre.conf --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2016ULpreVFPv15 --input-files inputs --max-memory 3000 --no-publication --dryrun
```

For Data:

```bash
python crab.py -p data_2018UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2016APV/data -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i data/data_2018.conf --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt' --work-area crab_projects_data_2018ULv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

python crab.py -p data_2017UL_NANO.py --site T2_CH_CERN -o /store/group/[outputpath]/2017/data -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i data/data_2017.conf --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt' --work-area crab_projects_data_2017ULv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

python crab.py -p data_2016ULpostVFP_NANO.py --site T2_CH_CERN -o /store/group/[outputpath]/2016/data -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i data/data_2016post.conf --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt' --work-area crab_projects_data_2016ULpostVFPv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

python crab.py -p data_2016ULpreVFP_NANO.py --site T2_CH_CERN -o /store/group/[outputpath]/2016APV/data -t NanoTuples-21Dec2025_Run2ULNanoAODv15 -i data/data_2016pre.conf --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt' --work-area crab_projects_data_2016ULpreVFPv15 --input-files inputs --max-memory 3000 --no-publication --dryrun
```

These commands will perform a "dryrun" to print out the CRAB configuration files. Please check everything is correct (e.g., the output path, version number, requested number of cores, etc.) before submitting the actual jobs. To actually submit the jobs to CRAB, just remove the `--dryrun` option at the end.

**Step 3**: check job status

The status of the CRAB jobs can be checked with:

```bash
./crab.py --status --work-area crab_projects_* --options "maxjobruntime=2500 maxmemory=3500" && ./crab.py --summary
```

Note that this will also **resubmit** failed jobs automatically.

The crab dashboard can also be used to get a quick overview of the job status:

- [https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11)

More options of this `crab.py` script can be found with:

```bash
./crab.py -h
```
