#! /bin/bash
# # ----------------------------------------
# # now for Run 3

# # MC, 2024 (used for all years with v15)
cmsDriver.py mc_2024_noak15_noscout --mc --era Run3_2024 --step NANO --conditions 150X_mcRun3_2024_realistic_v2 --datatier NANOAODSIM --eventcontent NANOAODSIM --fileout file:nano.root --filein file:inMINIAOD.root --no_exec -n -1 --nThreads 2

# ----------------------------------------
# now apply some customizations
# for cfg in $(ls mc*UL*.py); do
#     echo "Skimming genParticles in ${cfg}"
#     sed -i -e 's@# Customisation from command line@# Customisation from command line\nprocess.genParticleTable.cut = cms.string("(statusFlags.isFirstCopy() || statusFlags.isLastCopy()) \&\& (abs(pdgId) == 1 || abs(pdgId) == 2 || abs(pdgId) == 3 || abs(pdgId) == 4 || abs(pdgId) == 5 || abs(pdgId) == 6 || abs(pdgId) == 11 || abs(pdgId) == 13 || abs(pdgId) == 15 || abs(pdgId) == 24 || abs(pdgId) == 23 || abs(pdgId) == 25)")\n@' ${cfg}
# done

# append the following two lines to all configs
# from TopQuarkAnalysis.BFragmentationAnalyzer.customizeAddAll import customizeAddWeights
# customizeAddWeights(process, addClassicBFragAndDecay=True, addMLBfrag=True, addMLHdamp=True, addMLNNLO=True)
for cfg in $(ls mc_2024_noak15_noscout*.py); do
    echo "--- Adding B fragmentation and TOP ML weight customizations to ${cfg}"
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
