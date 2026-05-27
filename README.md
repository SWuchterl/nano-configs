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

The current version is based on the Run2UL config in `CMSSW_15_0_15_patch4`, but we use `CMSSW_15_0_17`, so it is based on [NanoAODv15](https://gitlab.cern.ch/cms-nanoAOD/nanoaod-doc/-/wikis/Releases/NanoAODv15) and runs for all eras.

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

Use EL8 or singularity container `cmssw-el8`:
```
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cmssw-el8
```

```bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
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
git clone ssh://git@gitlab.cern.ch:7999/tthcc-run-3/BFragmentationAnalyzer.git TopQuarkAnalysis/BFragmentationAnalyzer -b dev/CMSSW_15_0_17_nanoV15ExtSkim


# now the modified release for TOP weights and AK4Puppi ParT
git cms-merge-topic -u SWuchterl:dev/CMSSW_15_0_17_nanoV15ExtSkimLeptonParT

# and for the leptons (not needed anymore)
# git cms-merge-topic -u JulesVandenbroeck:dev/CMSSW_15_0_17_leptonParT

# get the jet ParT data files
git clone git@github.com:SWuchterl/RecoBTag-Combined-data.git -b dev/CMSSW_15_0_17_nanoV15ExtSkim RecoBTag/Combined/data/

# get the lepton PNET and ParT data files (nearly all)
git clone -b CMSSW_15_0_2_patchX_leptonParT git@github.com:JulesVandenbroeck/PhysicsTools-NanoAOD.git PhysicsTools/NanoAOD/data

# and compile
scram b -j8
cmsenv
```

## Production

**Step 0**: setup the crab production directory in `CMSSW_15_0_17/src` and set up grid proxy, CRAB environment, etc.

```bash
# set up grid proxy
voms-proxy-init -rfc -voms cms --valid 168:00
# set up CRAB env (must be done after cmsenv)
source /cvmfs/cms.cern.ch/common/crab-setup.sh
```

**Step 1**: clone the repo and generate the python config file with `generateConfigs.sh`:

```bash
git clone https://github.com/SWuchterl/nano-configs.git -b prod/CMSSW_15_0_17_nanoV15ExtSkim
cd nano-configs
./generateConfigs.sh
```

**Step 2**: use the `crab.py` script to submit the CRAB jobs:

For 2024:


```bash
./runT2B.sh 2024 --dryrun  # for T2B-USERS
./runLXplusBTV.sh 2024 --dryrun  # for LXPLUS-USERS THAT WRITE TO BTV /eos
./runLXplusT2_CH_CSCS.sh 2024 --dryrun  # for T2_CH_CSCS USERS
```

This command will perform a "dryrun" to print out the CRAB configuration files. Please check everything is correct (e.g., the output path, version number, requested number of cores, etc.) before submitting the actual jobs. Also check that the automatic generated sample list for your user are correct in `mc/mc_2024.conf` and `data/data_2024.conf` To actually submit the jobs to CRAB, just remove the `--dryrun` option at the end.

**Step 3**: check job status using mrCrabs

The status of the CRAB jobs can be checked using mrCrabs.
This will provide an overview of all the jobs submitted in the crab_projects folder

```bash
git clone git@github.com:CMS-L1T-Jet-Tagging/mrCrabs.git
python3 mrCrabs/mrCrabs.py crab_projects/*/crab_*
```
For resubmission of jobs in case of failed jobs (DISCLAIMER: only re-submit if few jobs fail due to access issues, in other cases talk with experts on why the jobs might have failed):

```bash
python3 mrCrabs/mrCrabs.py crab_projects/*/crab_* --resubmit
```

crab itself can also be used to get more detailed information on one submission in case of failed jobs:
```bash
crab status -d crab_projects/crab_projects_mc_2024v15/crab_project_sample_name
```
The crab dashboard can also be used to get a quick overview of the job status:

- [https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11)

More options of this `crab` script can be found with:

```bash
crab -h
```

## Alternative for resubmission: Use [mrCrabs](github.com:CMS-L1T-Jet-Tagging/mrCrabs)
```bash
git clone git@github.com:CMS-L1T-Jet-Tagging/mrCrabs.git
```
