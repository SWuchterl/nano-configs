
./crab.py -p mc_2024_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run3_v15_testLeptonParTV0/2024/mc -t NanoTuples-30Apr2026_Run3NanoAODv15 -i mc/mc_2024.conf -e exe_ULv15_noselnoskim.sh -s FileBased -n 2 --num-cores 1 --work-area crab_projects_2024v15V0 --input-files inputs --no-publication


./crab.py -p data_2024_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run3_v15_testLeptonParTV0/2024/data -t NanoTuples-30Apr2026_Run3NanoAODv15 -i data/data_2024.conf -e exe_ULv15_noselnoskim.sh -s FileBased -n 2 --num-cores 1 --work-area crab_projects_2024v15V0 --input-files inputs --no-publication
