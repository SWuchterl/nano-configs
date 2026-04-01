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

The current version is based on the Run3 config in CMSSW_15_0_17.

Customizations:

- Addition of the Muon+Electron ParticleNet ID
- Addition of the Muon+Electron ParticleTransformer ID
- Addint training nTuples for both

Current workflow: Do not regenerate the `mc_2024_NANO.py`

---

## Setup

```bash
cmsrel CMSSW_15_0_17
cd CMSSW_15_0_17/src
cmsenv
git cms-init

git cms-addpkg PhysicsTools/NanoAOD
git cms-addpkg PhysicsTools/PatAlgos
git cms-addpkg DataFormats/BTauReco

git cms-merge-topic -u SWuchterl:dev/CMSSW_15_0_17_leptonParT
# last commit should be 762aaec468a096d3fba0c476682d4c9174d8220c

git clone -b dev/CMSSW_15_0_2_patchX_leptonParT git@github.com:JulesVandenbroeck/PhysicsTools-NanoAOD.git PhysicsTools/NanoAOD/data
scram b -j8
```

## Production

**Step 0**: switch to the crab production directory and set up grid proxy, CRAB environment, etc.

```bash
# clone the repository
git clone -b dev/CMSSW_15_0_17_leptonParT git@github.com:SWuchterl/nano-configs.git
cd nano-configs

# set up grid proxy
voms-proxy-init -rfc -voms cms --valid 168:00
# set up CRAB env (must be done after cmsenv)
source /cvmfs/cms.cern.ch/common/crab-setup.sh
```

**Step 1**: generate the python config file with `generateConfigs.sh`.

**Step 2**: use the `crab.py` script to submit the CRAB jobs:

For MC:

```bash
python3 crab.py -p mc_2024_NANO.py --max-memory 2500 --site T2_BE_IIHE -o /store/group/[outputpath]/2024/mc -t NanoAODv15_leptonPNet -i mc/mc_2024.conf --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2024 --dryrun
```

For Data:

These commands will perform a "dryrun" to print out the CRAB configuration files. Please check everything is correct (e.g., the output path, version number, requested number of cores, etc.) before submitting the actual jobs. To actually submit the jobs to CRAB, just remove the `--dryrun` option at the end.

**Step 3**: check job status

The status of the CRAB jobs can be checked with:

```bash
./crab.py --status --work-area crab_projects_*  --options "maxjobruntime=2500 maxmemory=2500" && ./crab.py --summary
```

Note that this will also **resubmit** failed jobs automatically.

The crab dashboard can also be used to get a quick overview of the job status:

- [https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11](https://monit-grafana.cern.ch/d/cmsTMGlobal/cms-tasks-monitoring-globalview?orgId=11)

More options of this `crab.py` script can be found with:

```bash
./crab.py -h
```




# example submit
```bash
python3 crab.py \
    -p mc_2024_NANO.py \
    --site T2_CH_CERN \
    -o /eos/cms/store/group/cmst3/group/deepjet/leptonid/2024/mc_v3 \
    -t NanoAODv15_LeptonParT \
    -i mc/mc_2024.conf \
    -s FileBased -n 2 \
    --max-memory 2000 \
    --num-cores 1 --work-area crab_projects_2024 --no-publication
```