# parse --dryrun flag (remove it from positional args so $1 stays as the year)
DRYRUN=""
args=()
for arg in "$@"; do
    if [[ "$arg" == "--dryrun" ]]; then
        DRYRUN="--dryrun"
    else
        args+=("$arg")
    fi
done
set -- "${args[@]}"

if [[ $1 == 2024* ]]; then
    python crab.py \
        -p dataMuonPOG_2024_NANO_DQM.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuplesMuonPOG/2024/data \
        -t NanoTuplesMuonPOG-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2024.conf \
        -e exe_MuonPOG_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_dataMuonPOG_2024v15 \
        --input-files inputs \
        --max-memory 4500 --max-job-runtime 2750 $DRYRUN

    python crab.py \
        -p mcMuonPOG_2024_NANO_DQM.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuplesMuonPOG/2024/mc \
        -t NanoTuplesMuonPOG-uParTv3-parTlepID-NanoAODv15 \
        -i  mc/mc_2024.conf \
        -e exe_MuonPOG_ULv15_nosel.sh \
        --num-cores 2 \
        -s FileBased \
        -n 2 \
        --work-area crab_projects/crab_projects_mcMuonPOG_2024v15 \
        --input-files inputs \
        --max-memory 4500 --max-job-runtime 2750 $DRYRUN
fi 
if [[ $1 == 2025* ]]; then
    python crab.py \
        -p dataMuonPOG_2025_NANO_DQM.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuplesMuonPOG/2025/data \
        -t NanoTuplesMuonPOG-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2025.conf \
        -e exe_MuonPOG_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_dataMuonPOG_2025v15 \
        --input-files inputs \
        --max-memory 4500 --max-job-runtime 2750 $DRYRUN
fi 
if [[ $1 == 2022* ]]; then
    python crab.py \
        -p dataMuonPOG_2022_NANO_DQM.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuplesMuonPOG/2022/data \
        -t NanoTuplesMuonPOG-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2022.conf \
        -e exe_MuonPOG_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_dataMuonPOG_2022v15 \
        --input-files inputs \
        --max-memory 4500 --max-job-runtime 2750 $DRYRUN
fi 
if [[ $1 == 2023* ]]; then
    python crab.py \
        -p dataMuonPOG_2023_NANO_DQM.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuplesMuonPOG/2023/data \
        -t NanoTuplesMuonPOG-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2023.conf \
        -e exe_MuonPOG_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_dataMuonPOG_2023v15 \
        --input-files inputs \
        --max-memory 4500 --max-job-runtime 2750 $DRYRUN
fi
