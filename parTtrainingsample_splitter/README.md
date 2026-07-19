# parTtrainingsample_splitter

HTCondor workflow that merges the per-lepton ntuples spread across many
`tree_*.root` files and splits them into flat `.parquet` datasets for ParT
lepton-ID training.

Each input file holds two trees, `ntuplizer_muon/Events` and
`ntuplizer_electron/Events`, where **one entry = one lepton**. The workflow runs
for **one lepton flavor per run** and, **per sample**, splits every lepton into a
group defined by its gen-flavor category and pT range, writing each group to
parquet in shards of a configurable size.

## Splitting

- **pT** (`--pt-threshold`, default 35): `Lepton_pt >= thr` -> high, else low.
- **gen flavor** (`genPartFlav`): `1`=prompt, `15`=tau, `5`=heavy,
  `3 or 4`=light, everything else=fake.
- **Group folder**: `<category>_ptGe<thr>` or `<category>_ptLt<thr>`
  (e.g. `prompt_ptGe35`), 10 groups per sample.
- **Shard size** (`--leptons-per-group`, default 100000): once a group buffers
  this many leptons it is dumped to one parquet shard and the buffer is cleared;
  remainders are flushed at job end.

## Output layout

```
<outdir>/<sample>/<tag>/<group>/<flavor>_<sample>_batch<b>_shard<n>.parquet
<outdir>/<sample>/<tag>/summary/<flavor>_<sample>_batch<b>.json
```

`<tag>` is the production-tag folder (the directory right after the sample name
in the input path). If `<outdir>` starts with `root:` the files are copied with
`xrdcp -f -p`; otherwise they are written directly to the path.

Each job also writes one **summary JSON** into a `summary/` folder next to the
group folders, recording the lepton count in every category group for that job
(0 when the job produced none). Combine them across all jobs and samples with
`combine_summaries.py` for a total view of the training statistics.

## Components

| file | role |
|------|------|
| `discover_samples.py` | list files per sample via `xrdfs`, chunk into batches, write filelists + `work/manifest.json` |
| `submit_condor.py`    | generate one condor submit file per sample and submit (or `--dry-run` / `--submit-test` / `--local-test`) |
| `merge_ntuples.py`    | the per-job worker: xrdcp -> uproot read in entry batches -> split -> `ak.to_parquet`; also writes a per-job `summary/*.json` of lepton counts |
| `combine_summaries.py`| combine every `summary/*.json` across all jobs & samples into one total-count view (local path or `root://` tree) |
| `run_job.sh`          | condor executable; builds a **fresh** CMSSW_15_0_17 (`cmsrel`) then calls `merge_ntuples.py` |
| `run_splitter.sh`     | convenience wrapper (uses the CMSSW env `python3`): discover then submit |

## Environments

- **Local (submission + local testing)** — run from inside the **CMSSW_15_0_17**
  environment (`cmsenv`), which provides `python3` + uproot/awkward/pyarrow/numpy.
  Local testing runs on **local** `.root` files and never uses `xrdcp`/`xrdfs`.
  Note: awkward 2.6.3 can `ak.to_parquet` (write) fine, but `ak.from_parquet`
  (read-back) fails against the env's pyarrow 21 (`pyarrow.lib.PyExtensionType`
  removed); read shards back with `pyarrow.parquet.read_table` for verification.
- **Condor worker (the real merge)** — each job builds a **fresh** CMSSW_15_0_17
  on the node (`export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch;
  source $VO_CMS_SW_DIR/cmsset_default.sh; cmsrel CMSSW_15_0_17;
  cd CMSSW_15_0_17/src; cmsenv`), which provides python3 + uproot/awkward/numpy
  **and** `xrdcp`. Nothing CMSSW-related is passed from the submit side.

Jobs are split into batches of 100 files (`--files-per-batch`) so merging within
a sample runs in parallel. Each batch is one condor job; all batches of a sample
share `JobBatchName = parTsplit_<flavor>_<sample>`. Sharding is per-batch (no
cross-batch reduce), so the exact `--leptons-per-group` size is enforced only
within a job.

## Memory / disk behaviour

- Files are processed **one at a time**, with a **one-deep prefetch**: while file
  N is being read, file N+1 is `xrdcp`'d in the background (local files are read
  in place). The current local copy is deleted right after reading, so at most two
  remote files sit on scratch at once.
- Each tree is read in entry batches (`--read-step`, default 100000 — one batch
  per ~60k-lepton file).
- **Total buffered leptons are capped** by `--max-buffer` (default 1.5M): when the
  buffer exceeds the cap the **largest** group is flushed to a shard. Without this,
  low-population groups (e.g. `tau_ptGe35`) would buffer their full nested records
  for the whole job — a 100-file job was observed ratcheting to ~337 GB RSS. The
  cap bounds RAM (condor `request_memory` default is 16 GB); `--max-buffer` /
  `--read-step` can be lowered to fit a tighter slot.
- Splitting each chunk into groups is a single stable-argsort gather (one
  full-record materialization per read batch), not a per-group boolean scan.
- Because the cap can flush a group early, a group may end up in several shards;
  this does not change the per-group lepton totals (downstream reads all shards in
  the group folder).

## Usage

```bash
# 0) one-time: enter the CMSSW_15_0_17 environment (provides python3 + deps)
cd CMSSW_15_0_17/src && cmsenv && cd -

# 1) LOCAL test on local .root file(s) — no condor, no xrdcp:
./run_splitter.sh muon ./localtest_out --local-test --local-input /path/to/tree_1.root
#    --local-input accepts a .root file, a directory, or a .txt filelist;
#    --local-test-files N caps how many are used (default 2).

# 2) single-job condor test: submit ONE real job (first batch of first sample):
./run_splitter.sh muon root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit \
    --sample 'TTTT*' --submit-test
#    ...then track it:  condor_q -batch

# 3) dry-run condor submission (write .sub, do not submit):
python3 discover_samples.py --sample 'TTTT*'
python3 submit_condor.py --flavor electron \
    --outdir root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit \
    --sample 'TTTT*' --dry-run

# 4) full run (all samples, one flavor):
./run_splitter.sh muon root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit
./run_splitter.sh electron root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit

# 5) once jobs finish: total lepton counts across all jobs & samples:
python3 combine_summaries.py root://maite.iihe.ac.be/pnfs/iihe/cms/store/user/$USER/parTsplit
#    (or a local outdir) -> prints a table and writes combined_summary.json
```

Run the scripts from inside the CMSSW_15_0_17 environment (`cmsenv`); `python3`
then resolves to the CMSSW python that carries uproot/awkward/pyarrow/numpy, and
`run_splitter.sh` uses it automatically.

`--submit-test` is the recommended smoke test before a full run: it exercises the
complete condor round-trip (submit file generation + `condor_submit` + the worker
building a fresh CMSSW + xrdcp read + parquet write to `--outdir`) for a single
batch, so a successful job confirms the whole chain end-to-end.

Track jobs with `condor_q -batch` (batch names are `parTsplit_<flavor>_<sample>`).
