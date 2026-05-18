# python3 crab.py -p mc_2017UL_NANO.py --max-memory 2500 --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2017/mc -t NanoTuples-May2026_Run2ULNanoAODv15 -i mc/mc_2017.conf --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2017ULv15 --dryrun

# ./crab.py --private-mc -p FAKEMiniAODv2_cfg.py --site T2_CH_CERN -o /store/group/cmst3/group/some/path/to/final/dist/2017/mc -t RunIISummer20UL17MiniAODv2 -i samples/mc_2017.conf -e exe.sh --script-args beginseed=0 -s EventBased -n 1000 --max-units 1000000 --input-files inputs --max-memory 10000 --num-cores 4 --work-area crab_projects_2017_mc_run1 --dryrun

# real submit commands:
# python crab.py -p data_2017UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2017/data -t NanoTuples-May2026_Run2ULNanoAODv15 -i data/data_2017.conf -e exe_ULv15.sh --num-cores 4 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt' --work-area crab_projects_data_2017ULv15 --input-files inputs --max-memory 6000 --no-publication

# ./crab.py -p mc_2017UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2017/mc -t NanoTuples-May2026_Run2ULNanoAODv15 -i  mc/mc_2017.conf -e exe_ULv15.sh -s FileBased -n 2 --num-cores 4 --work-area crab_projects_2017ULv15 --input-files inputs --max-memory 6000 --no-publication






# now let's test all years
# data, 2016ULpreVFP
python crab.py -p data_2016ULpreVFP_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2016ULpreVFP/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2016pre.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt' --work-area crab_projects_v15TestAll_data_2016ULv15 --input-files inputs --max-memory 3000 --no-publication

# data, 2016ULpostVFP
python crab.py -p data_2016ULpostVFP_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2016ULpostVFP/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2016post.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt' --work-area crab_projects_v15TestAll_data_2016ULv15 --input-files inputs --max-memory 3000 --no-publication

# data, 2017
python crab.py -p data_2017UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2017/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2017.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt' --work-area crab_projects_v15TestAll_data_2017ULv15 --input-files inputs --max-memory 3000 --no-publication

# data, 2018
python crab.py -p data_2018UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2018/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2018.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 -j 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt' --work-area crab_projects_v15TestAll_data_2018ULv15 --input-files inputs --max-memory 3000 --no-publication

# data, 2022
python crab.py -p data_2022_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2022/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2022.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 --work-area crab_projects_v15TestAll_data_2022ULv15 --input-files inputs --max-memory 3000 --no-publication

# data, 2023
python crab.py -p data_2023_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2023/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2023.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 --work-area crab_projects_v15TestAll_data_2023ULv15 --input-files inputs --max-memory 3000 --no-publication

# data, 2024
python crab.py -p data_2024_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run3-v15ext/2024/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2024.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 --work-area crab_projects_data_2024v15 --input-files inputs --max-memory 3000 --no-publication

# data, 2025
python crab.py -p data_2025_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/v15TestAll/2025/data -t NanoTuples-May2026_NanoAODv15 -i data/data_2025.conf -e exe_ULv15_nosel.sh --num-cores 1 -s EventAwareLumiBased -n 100000 --work-area crab_projects_v15TestAll_data_2025ULv15 --input-files inputs --max-memory 3000 --no-publication


# MC, 2016ULpreVFP
python3 crab.py -p mc_2016ULpreVFP_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2016APV/mc -t NanoTuples-May2026_NanoAODv15 -i mc/mc_2016pre.conf -e exe_ULv15_nosel.sh --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2016ULpreVFPv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

# MC, 2016ULpostVFP
python3 crab.py -p mc_2016ULpostVFP_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2016/mc -t NanoTuples-May2026_NanoAODv15 -i mc/mc_2016post.conf -e exe_ULv15_nosel.sh --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2016ULpostVFPv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

# MC, 2017
./crab.py -p mc_2017UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2017/mc -t NanoTuples-May2026_NanoAODv15 -i mc/mc_2017.conf -e exe_ULv15_nosel.sh -s FileBased -n 2 --num-cores 1 --work-area crab_projects_2017ULv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

# MC, 2018
python3 crab.py -p mc_2018UL_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run2ULPuppi-v15ext/2018/mc -t NanoTuples-May2026_NanoAODv15 -i mc/mc_2018.conf -e exe_ULv15_nosel.sh --num-cores 1 -s FileBased -n 2 --work-area crab_projects_2018ULv15 --input-files inputs --max-memory 3000 --no-publication --dryrun

# MC, 2024
python3 crab.py -p mc_2024_NANO.py --site T2_CH_CERN -o /store/group/cmst3/group/vhcc/NanoAOD/dev_Run3-v15extV0/2024/mc -t NanoTuples-23Apr2026_NanoAODv15 -i  mc/mc_2024.conf -e exe_ULv15_nosel.sh -s FileBased -n 2 --num-cores 1 --work-area crab_projects_2024v15V0 --input-files inputs --no-publication