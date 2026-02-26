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

The current version is based on the Run3 config in CMSSW_15_0_2.

Customizations:

- Addition of the Electron ParticleNet ID

---

## Setup

```bash
cmsrel CMSSW_15_0_2
cd CMSSW_15_0_2/src
cmsenv

git cms-merge-topic -u JulesVandenbroeck:CMSSW_15_0_2_patchX_leptonPNet
scram b -j8
```

## Production

**Step 0**: switch to the crab production directory and set up grid proxy, CRAB environment, etc.

```bash
# clone the repository
git clone -b dev/CMSSW_15_0_2/leptonPNet git@github.com:hqucms/nano-configs.git
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
