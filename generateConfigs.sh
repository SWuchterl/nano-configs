#! /bin/bash

# technically CMSSW_15_0_15_patch4 but we use the same for 15_0_17

# # MC, 2018UL
cmsDriver.py mc_2018UL --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mc2018_realistic_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec -n -1

# # Data, 2018UL
cmsDriver.py data_2018UL --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec -n -1

# MC, 2017UL
cmsDriver.py mc_2017UL --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mc2017_realistic_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec -n -1

# # Data, 2017UL
cmsDriver.py data_2017UL --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec -n -1

# # MC, 2016ULpreVFP
cmsDriver.py mc_2016ULpreVFP --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mcRun2_asymptotic_preVFP_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec -n -1

# # Data, 2016ULpreVFP
cmsDriver.py data_2016ULpreVFP --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec -n -1

# # MC, 2016ULpostVFP
cmsDriver.py mc_2016ULpostVFP --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mcRun2_asymptotic_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec -n -1

# # Data, 2016ULpostVFP
cmsDriver.py data_2016ULpostVFP --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec -n -1


# ----------------------------------------
# now apply some customizations

for cfg in $(ls mc*UL*.py); do
    echo "Skimming genParticles in ${cfg}"
    sed -i -e 's@# Customisation from command line@# Customisation from command line\nprocess.genParticleTable.cut = cms.string("(statusFlags.isFirstCopy() || statusFlags.isLastCopy()) \&\& (abs(pdgId) == 1 || abs(pdgId) == 2 || abs(pdgId) == 3 || abs(pdgId) == 4 || abs(pdgId) == 5 || abs(pdgId) == 6 || abs(pdgId) == 11 || abs(pdgId) == 13 || abs(pdgId) == 15 || abs(pdgId) == 24 || abs(pdgId) == 23 || abs(pdgId) == 25)")\n@' ${cfg}
done
