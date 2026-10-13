
DRYRUN=""
PREPARE_RECOVERY_TASK=""
SUBMIT_RECOVERY_TASK=""
RECOVERY_PREFIX=""
SWITH_TO_FILEBASED=""
FORCE=""

args=()
for arg in "$@"; do
    if [[ "$arg" == "--dryrun" ]]; then
        DRYRUN="--dryrun"
    fi
    if [[ "$arg" == "--prepare-recovery-task" ]]; then
        PREPARE_RECOVERY_TASK="--prepare-recovery-task"
        RECOVERY_PREFIX="--recovery-task-suffix _filebased_v3"
    fi
    if [[ "$arg" == "--submit-recovery-task" ]]; then
        SUBMIT_RECOVERY_TASK="--submit-recovery-task"
        RECOVERY_PREFIX="--recovery-task-suffix _filebased_v3"
    fi
    if [[ "$arg" == "--switch-to-filebased" ]]; then
        SWITH_TO_FILEBASED="--switch-to-filebased"
    fi
    if [[ "$arg" == "--force" && -n "$RECOVERY_PREFIX" ]]; then
        FORCE="--yes"
    else
        args+=("$arg")
    fi
done
set -- "${args[@]}"

python3 sampleGeneration.py $1 --user $USER --skip-check


if [[ $1 == 2018* ]]; then
    python3 crab.py \
        -p data_2018UL_NANO.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuples/2018/data \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i data/data_2018.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s EventAwareLumiBased \
        -n 100000 \
        --work-area crab_projects/crab_projects_data_2018v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE \
        $SWITH_TO_FILEBASED

    python3 crab.py \
        -p mc_2018UL_NANO.py \
        --site T2_BE_IIHE \
        -o /store/group/CustomNanoAODv15/NanoTuples/2018/mc \
        -t NanoTuples-uParTv3-parTlepID-NanoAODv15 \
        -i  mc/mc_2018.conf \
        -e exe_ULv15_nosel.sh \
        --num-cores 2 \
        -s FileBased \
        -n 2 \
        --work-area crab_projects/crab_projects_mc_2018v15 \
        --input-files inputs \
        --max-memory 4500 \
        --max-job-runtime 2750 \
        $DRYRUN \
        $PREPARE_RECOVERY_TASK \
        $SUBMIT_RECOVERY_TASK \
        $RECOVERY_PREFIX $FORCE \
        $SWITH_TO_FILEBASED
fi 
