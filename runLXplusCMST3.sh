# parse --dryrun flag (remove it from positional args so $1 stays as the year)
args=()
for arg in "$@"; do
    if [[ "$arg" == "--dryrun" ]]; then
        DRYRUN="--dryrun"
    fi
    if [[ "$arg" == "--prepare-recovery-task" ]]; then
        PREPARE_RECOVERY_TASK="--prepare-recovery-task"
        RECOVERY_PREFIX="--recovery-task-suffix _recovery_v1"
    fi
    if [[ "$arg" == "--submit-recovery-task" ]]; then
        SUBMIT_RECOVERY_TASK="--submit-recovery-task"
        RECOVERY_PREFIX="--recovery-task-suffix _recovery_v1"
    fi
    if [[ "$arg" == "--force" && -n "$RECOVERY_PREFIX" ]]; then
        FORCE="--yes"
    else
        args+=("$arg")
    fi
done
set -- "${args[@]}"

# python3 sampleGeneration.py $1 --user $USER --skip-check

if [[ $1 == 2024* ]]; then
    python3 crab.py \
        -p data_2024_NANO.py \
        --site T2_CH_CERN \
        -o /store/group/cmst3/group/vhcc/NanoAOD/NanoTuples/2024/data \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2024.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_data_2024v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE

    python3 crab.py \
        -p mc_2024_NANO.py \
        --site T2_CH_CERN \
        -o /store/group/cmst3/group/vhcc/NanoAOD/NanoTuples/2024/mc \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i  mc/mc_2024.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s FileBased \
        -n 2 \
        --work-area crab_projects/crab_projects_mc_2024v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE
fi 
if [[ $1 == 2025* ]]; then
    python3 crab.py \
        -p data_2025_NANO.py \
        --site T2_CH_CERN \
        -o /store/group/cmst3/group/vhcc/NanoAOD/NanoTuples/2025/data \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2025.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_data_2025v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE
fi 
if [[ $1 == 2022* ]]; then
    python3 crab.py \
        -p data_2022_NANO.py \
        --site T2_CH_CERN \
        -o /store/group/cmst3/group/vhcc/NanoAOD/NanoTuples/2022/data \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2022.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_data_2022v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE
fi 
if [[ $1 == 2023* ]]; then
    python3 crab.py \
        -p data_2023_NANO.py \
        --site T2_CH_CERN \
        -o /store/group/cmst3/group/vhcc/NanoAOD/NanoTuples/2023/data \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2023.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_data_2023v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE
fi
