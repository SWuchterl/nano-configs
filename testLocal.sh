#!/bin/bash -x

# cmsRun mc_2024_NANO.py

# # outputfile is called nano.root
# # rename it
# cp nano.root nano_noskim.root
cp -f nano_noskim.root nano.root

# rm nano.root

# 2) postprocessing with nano_postproc.py

# run the postprocessor with the final selection
nano_postproc.py . nano_noskim.root -s _keepdrop --bi inputs/keep_and_drop.txt

# now merge the output files into one final nanoAOD file to reduce size
haddnano.py final.root nano_noskim_keepdrop.root

# now name the new one nano.root
# mv final.root nano.root

# that one should be copied now by crab