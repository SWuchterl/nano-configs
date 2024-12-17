#! /bin/bash

# MC, 2018UL
cmsDriver.py mc_2018UL --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 106X_upgrade2018_realistic_v16_L1v1 --step NANO --filein file:inMINIAOD.root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec -n -1

# Data, 2018UL
cmsDriver.py data_2018UL --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 106X_dataRun2_v36 --step NANO --filein file:inMINIAOD.root --era Run2_2018,run2_nanoAOD_106Xv2 --no_exec -n -1

# MC, 2017UL
cmsDriver.py mc_2017UL --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 106X_mc2017_realistic_v10 --step NANO --filein file:inMINIAOD.root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec -n -1

# Data, 2017UL
cmsDriver.py data_2017UL --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 106X_dataRun2_v36 --step NANO --filein file:inMINIAOD.root --era Run2_2017,run2_nanoAOD_106Xv2 --no_exec -n -1

# MC, 2016ULpreVFP
cmsDriver.py mc_2016ULpreVFP --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 106X_mcRun2_asymptotic_preVFP_v11 --step NANO --filein file:inMINIAOD.root --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec -n -1

# Data, 2016ULpreVFP
cmsDriver.py data_2016ULpreVFP --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 106X_dataRun2_v36 --step NANO --filein file:inMINIAOD.root --era Run2_2016_HIPM,run2_nanoAOD_106Xv2 --no_exec -n -1

# MC, 2016ULpostVFP
cmsDriver.py mc_2016ULpostVFP --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 106X_mcRun2_asymptotic_v17 --step NANO --filein file:inMINIAOD.root --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec -n -1

# Data, 2016ULpostVFP
cmsDriver.py data_2016ULpostVFP --data --eventcontent NANOAOD --datatier NANOAOD --fileout file:nano.root --conditions 106X_dataRun2_v36 --step NANO --filein file:inMINIAOD.root --era Run2_2016,run2_nanoAOD_106Xv2 --no_exec -n -1

for cfg in $(ls *UL*.py); do
    echo "Adding ParticleNetAK4 Run2UL to ${cfg}"
    sed -i -e 's@# Customisation from command line@# Customisation from command line\nfrom RecoBTag.ONNXRuntime.pfParticleNetAK4_cff import _pfParticleNetAK4JetTagsProbs\nfrom PhysicsTools.NanoAOD.common_cff import Var\nfor prob in _pfParticleNetAK4JetTagsProbs:\n    name = "ParticleNetAK4_" + prob.split(":")[1]\n    setattr(process.jetPuppiTable.variables, name, Var("bDiscriminator('"'"'%s'"'"')" % prob, float, doc=prob, precision=-1))\n@' ${cfg}
done

for cfg in $(ls mc*UL*.py); do
    echo "Adding AK4 nBHadrons/nCHadrons to ${cfg}"
    sed -i -e 's@# Customisation from command line@# Customisation from command line\nfrom PhysicsTools.NanoAOD.common_cff import Var\nprocess.jetMCTable.variables.nBHadrons = Var("jetFlavourInfo().getbHadrons().size()", "uint8", doc="number of b-hadrons")\nprocess.jetMCTable.variables.nCHadrons = Var("jetFlavourInfo().getcHadrons().size()", "uint8", doc="number of c-hadrons")\n@' ${cfg}
done

for cfg in $(ls mc*UL*.py); do
    echo "Adding all PS weights to ${cfg}"
    sed -i -e 's@# Customisation from command line@# Customisation from command line\nprocess.genWeightsTable.keepAllPSWeights = cms.bool(True)\n@' ${cfg}
done
