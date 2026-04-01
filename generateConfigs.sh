#! /bin/bash

# MC, 2024
cmsDriver.py mc_2024 \
--mc \
--step NANO \
--conditions 150X_mcRun3_2024_realistic_v2 \
--datatier NANOAODSIM \
--era Run3_2024 \
--eventcontent NANOAODSIM \
--filein "file:inMINIAOD.root" \
--fileout file:nano.root \
--geometry DB:Extended \
--no_exec -n -1 \


#---------------------------
# originally in addition used by Kiril:
# --customise_commands "process.packedpuppi.useExistingWeights=False \n process.packedpuppiNoLep.useExistingWeights=False \n from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD; runMetCorAndUncFromMiniAOD(process,isData=False,jetCollUnskimmed='updatedJetsPuppi',metType='Puppi',postfix='Puppi',jetFlavor='AK4PFPuppi',puppiProducerLabel='packedpuppi',puppiProducerForMETLabel='packedpuppiNoLep',recoMetFromPFCs=True) " \
# --step NANO:@JME


# # MC, 2024
# cmsDriver.py mc_2024 \
# --mc \
# --conditions 150X_mcRun3_2024_realistic_v2 \
# --datatier NANOAODSIM \
# --era Run3_2024 \
# --eventcontent NANOAODSIM \
# --customise_commands "process.packedpuppi.useExistingWeights=False \n process.packedpuppiNoLep.useExistingWeights=False \n from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD; runMetCorAndUncFromMiniAOD(process,isData=False,jetCollUnskimmed='updatedJetsPuppi',metType='Puppi',postfix='Puppi',jetFlavor='AK4PFPuppi',puppiProducerLabel='packedpuppi',puppiProducerForMETLabel='packedpuppiNoLep',recoMetFromPFCs=True) " \
# --filein "file:inMINIAOD.root" \
# --fileout file:nano.root \
# --geometry DB:Extended \
# --no_exec -n -1 \
# --step NANO:@JME
