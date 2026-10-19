# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: mc_2024 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --fileout file:nano.root --conditions 150X_mcRun3_2024_realistic_v2 --step NANO --filein file:inMINIAOD.root --era Run3_2024 --geometry DB:Extended --no_exec -n -1 --nThreads 2
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run3_2024_cff import Run3_2024

process = cms.Process('NANO',Run3_2024)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 1000  # small CRAB job logs (the schedd disk was full on 2026-10-12)
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:inMINIAOD.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('mc_2024 nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:nano.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '150X_mcRun3_2024_realistic_v2', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

#Setup FWK for multithreaded
process.options.numberOfThreads = 2
process.options.numberOfStreams = 0

# customisation of the process.

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon

# training ntuples: do not re-evaluate the AK4 jet taggers (about 60% of the CPU time);
# the lepton features use only the jet kinematics, the jets come directly from MiniAOD
from PhysicsTools.NanoAOD.jetsAK4_Puppi_cff import nanoAOD_addDeepInfoAK4_switch
for _sw in ['nanoAOD_addParticleNet_switch', 'nanoAOD_addRobustParTAK4Tag_switch',
            'nanoAOD_addUnifiedParTAK4Tag_switch', 'nanoAOD_addNoPIDParTAK4Tag_switch']:
    setattr(nanoAOD_addDeepInfoAK4_switch, _sw, cms.untracked.bool(False))

#call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeCommon(process)

# re-apply the AK4 Puppi JEC from the global tag exactly as nanoAOD_addDeepInfoAK4 does, without the taggers
from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
from PhysicsTools.PatAlgos.tools.helpers import getPatAlgosToolsTask, addToProcessAndTask
updateJetCollection(
    process,
    jetSource=cms.InputTag('slimmedJetsPuppi', processName=cms.InputTag.skipCurrentProcess()),
    jetCorrections=('AK4PFPuppi', cms.vstring(['L2Relative', 'L3Absolute']), 'None'),
    postfix='PuppiWithDeepInfo',
)
addToProcessAndTask("slimmedJetsPuppi", process.selectedUpdatedPatJetsPuppiWithDeepInfo.clone(), process,
                    getPatAlgosToolsTask(process))
del process.selectedUpdatedPatJetsPuppiWithDeepInfo

# End of customisation functions


# Customisation from command line
from ParticleNetNtuplizer.ParticleNetNtuplizer.electron_ntuplizer import customize_training_ntuplizer as customize_ntuplizer_electron
from ParticleNetNtuplizer.ParticleNetNtuplizer.muon_ntuplizer import customize_training_ntuplizer as customize_ntuplizer_muon

# which trees to write: leptons=both (default), electron or muon (CRAB: pyCfgParams, local: cmsRun mc_2024_NANO.py leptons=muon)
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing()
options.register('leptons', 'both', VarParsing.multiplicity.singleton, VarParsing.varType.string,
                 'training trees to write: both, electron or muon')
options.parseArguments()
if options.leptons not in ('both', 'electron', 'muon'):
    raise ValueError("leptons must be both, electron or muon, got '%s'" % options.leptons)
writeElectronTree = options.leptons in ('both', 'electron')
writeMuonTree = options.leptons in ('both', 'muon')

if writeElectronTree:
    process = customize_ntuplizer_electron(process)
if writeMuonTree:
    process = customize_ntuplizer_muon(process)

process.schedule.remove(process.NANOAODSIMoutput_step)
del process.NANOAODSIMoutput_step
del process.NANOAODSIMoutput

process.source.delayReadingEventProducts = cms.untracked.bool(False)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
