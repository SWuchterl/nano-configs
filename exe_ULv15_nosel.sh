#!/bin/bash -x

JOBINDEX=${1##*=} # hard coded by crab
NEVENTS=${2##*=}  # ordered by crab.py script
NTHREAD=${3##*=}  # ordered by crab.py script
NAME=${4##*=}     # ordered by crab.py script

WORKDIR=$(pwd)

# 1) run the actual nanoAOD step first
cmsRun -j FrameworkJobReport.xml PSet.py

# outputfile is called nano.root
# rename it
mv nano.root orig_nano.root

# 2) postprocessing with nano_postproc.py

# run the postprocessor with the final selection
nano_postproc.py . orig_nano.root -s _keepdrop --bi $WORKDIR/inputs/keep_and_drop.txt

# now merge the output files into one final nanoAOD file to reduce size
haddnano.py final.root orig_nano_keepdrop.root

# now name the new one nano.root
mv final.root nano.root

# that one should be copied now by crab