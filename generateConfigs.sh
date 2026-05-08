#! /bin/bash

# technically CMSSW_15_0_15_patch4 but we use the same for 15_0_17

# # MC, 2018UL
cmsDriver.py mc_2018UL --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mc2018_realistic_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec -n -1

# # # Data, 2018UL
cmsDriver.py data_2018UL --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec -n -1

# # MC, 2017UL
cmsDriver.py mc_2017UL --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mc2017_realistic_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec -n -1

# # # Data, 2017UL
cmsDriver.py data_2017UL --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec -n -1

# # # MC, 2016ULpreVFP
cmsDriver.py mc_2016ULpreVFP --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mcRun2_asymptotic_preVFP_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec -n -1

# # # Data, 2016ULpreVFP
cmsDriver.py data_2016ULpreVFP --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec -n -1

# # # MC, 2016ULpostVFP
cmsDriver.py mc_2016ULpostVFP --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mcRun2_asymptotic_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec -n -1

# # # Data, 2016ULpostVFP
cmsDriver.py data_2016ULpostVFP --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 150X_dataRun2_v1 --step NANO --filein file:inMINIAOD.root --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec -n -1

# ----------------------------------------
# now for Run 3

# MC, 2024
cmsDriver.py mc_2024 --mc --era Run3_2024 --step NANO --conditions 150X_mcRun3_2024_realistic_v2 --datatier NANOAODSIM --eventcontent NANOAODSIM --fileout file:nano.root --filein file:inMINIAOD.root --no_exec -n -1

# Data, 2024
cmsDriver.py data_2024 --data --era Run3_2024 --step NANO --conditions 150X_dataRun3_v2 --datatier NANOAOD --eventcontent NANOAOD --fileout file:nano.root --filein file:inMINIAOD.root --no_exec -n -1

# ----------------------------------------
# now apply some customizations
# for cfg in $(ls mc*UL*.py); do
#     echo "Skimming genParticles in ${cfg}"
#     sed -i -e 's@# Customisation from command line@# Customisation from command line\nprocess.genParticleTable.cut = cms.string("(statusFlags.isFirstCopy() || statusFlags.isLastCopy()) \&\& (abs(pdgId) == 1 || abs(pdgId) == 2 || abs(pdgId) == 3 || abs(pdgId) == 4 || abs(pdgId) == 5 || abs(pdgId) == 6 || abs(pdgId) == 11 || abs(pdgId) == 13 || abs(pdgId) == 15 || abs(pdgId) == 24 || abs(pdgId) == 23 || abs(pdgId) == 25)")\n@' ${cfg}
# done

# append the following two lines to all configs
# from TopQuarkAnalysis.BFragmentationAnalyzer.customizeAddAll import customizeAddWeights
# customizeAddWeights(process, addClassicBFragAndDecay=True, addMLBfrag=True, addMLHdamp=True, addMLNNLO=True)
for cfg in $(ls mc*.py); do
    echo "Adding B fragmentation and TOP ML weight customizations to ${cfg}"
    sed -i -e '/# Customisation from command line/a from TopQuarkAnalysis.BFragmentationAnalyzer.customizeAddAll import customizeAddWeights\ncustomizeAddWeights(process, addClassicBFragAndDecay=True, addClassicCFragAndDecay=True, addMLBfrag=True, addMLHdamp=True, addMLNNLO=True)\n' ${cfg}
done

# ----------------------------------------

# in case, for testing 2024
# process.source.fileNames = cms.untracked.vstring(
#     '/store/mc/RunIII2024Summer24MiniAODv6/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/MINIAODSIM/150X_mcRun3_2024_realistic_v2-v2/2810003/7fe77f65-f0aa-47f6-a04b-25ba43dd6737.root',
# )

# process.maxEvents.input = 1000

# # dump configuration to file dump.py
# with open('dump.py', 'w') as f:
#     f.write(process.dumpPython())