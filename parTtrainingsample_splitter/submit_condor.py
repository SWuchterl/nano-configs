#!/usr/bin/env python3
"""Generate and submit HTCondor jobs for the ntuple splitter.

Reads the manifest produced by ``discover_samples.py`` and writes one HTCondor
submit file per sample that bundles all of that sample's batch jobs (one job per
100-file batch). The job name carries the sample so a whole sample can be tracked
with ``condor_q -batch``.

Modes:
  (default)     write submit files and run ``condor_submit`` for each sample.
  --dry-run     write submit files and print the commands, but do not submit.
  --submit-test submit only the first batch of the first matched sample.
  --local-test  skip condor entirely and run merge_ntuples.py in-process on a few
                LOCAL .root files (``--local-input``) to validate the
                read -> split -> parquet path. Local testing never uses xrdcp/xrdfs
                (those are only needed inside condor jobs, via the fresh CMSSW).

The condor jobs build a fresh CMSSW_15_0_17 on the worker (see run_job.sh), so no
CMSSW path is passed from here.
"""
import argparse
import fnmatch
import glob as globmod
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
MERGE_SCRIPT = os.path.join(HERE, "merge_ntuples.py")
RUN_JOB = os.path.join(HERE, "run_job.sh")

SUBMIT_TEMPLATE = """\
executable            = {run_job}
universe              = vanilla
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
{x509}transfer_input_files  = {merge_script}, $(filelist_path)
arguments             = {flavor} $(sample) $(tag) $(batch_id) $(filelist_basename) {outdir} {pt_threshold} {leptons_per_group}
JobBatchName          = parTsplit_{flavor}_{sample}
output                = {logdir}/batch_$(batch_id).out
error                 = {logdir}/batch_$(batch_id).err
log                   = {logdir}/cluster.log
request_memory        = {request_memory}
request_disk          = {request_disk}
+MaxRuntime           = {max_runtime}

queue sample, tag, batch_id, filelist_basename, filelist_path from {queue_file}
"""


def stage_proxy(dest_dir):
    """Copy the grid proxy into ``dest_dir`` and return the copy's path (or None).

    Uses $X509_USER_PROXY when set, otherwise the standard ``/tmp/x509up_u<uid>``
    location. Condor cannot always read the proxy straight from ``/tmp`` (private,
    per-node ``/tmp``), so we stage a copy in the readable work dir and hand the
    job that copy; it is shipped to the worker where ``xrdcp`` authenticates.
    """
    src = os.environ.get("X509_USER_PROXY") or "/tmp/x509up_u{}".format(os.getuid())
    if not os.path.exists(src):
        return None
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "x509up_proxy")
    shutil.copyfile(src, dest)
    os.chmod(dest, 0o600)
    return dest


def x509_block(proxy_dir):
    """Submit-file lines that ship the staged grid proxy to the worker (or '')."""
    proxy = stage_proxy(proxy_dir)
    if proxy is None:
        print("[warn] no X509 proxy found (set X509_USER_PROXY or run voms-proxy-init); "
              "jobs that xrdcp remote files/outputs will fail auth.", file=sys.stderr)
        return ""
    print("[proxy] staged grid proxy -> {}".format(proxy))
    return ("use_x509userproxy     = True\n"
            "x509userproxy         = {}\n".format(proxy))


def load_manifest(path):
    with open(path) as fh:
        return json.load(fh)


def select(manifest, patterns):
    if not patterns:
        return manifest
    return [j for j in manifest if any(fnmatch.fnmatch(j["sample"], p) for p in patterns)]


def by_sample(jobs):
    out = {}
    for j in jobs:
        out.setdefault(j["sample"], []).append(j)
    return out


def gather_local_root_files(path):
    """Return a list of local .root files from a file, directory, or .txt filelist."""
    if os.path.isdir(path):
        return sorted(globmod.glob(os.path.join(path, "**", "*.root"), recursive=True))
    if path.endswith(".txt"):
        with open(path) as fh:
            return [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    if path.endswith(".root"):
        return [path]
    # glob pattern fallback
    return sorted(globmod.glob(path))


def local_test(args):
    """Run merge_ntuples.py on a few LOCAL .root files (no xrdcp/xrdfs)."""
    if not args.local_input:
        print("[error] --local-test requires --local-input <file|dir|filelist.txt> "
              "of LOCAL .root files (local testing does not use xrdcp)", file=sys.stderr)
        return 1
    files = gather_local_root_files(args.local_input)
    if not files:
        print("[error] no .root files found at {}".format(args.local_input), file=sys.stderr)
        return 1
    files = files[: args.local_test_files]

    workdir = os.path.join(HERE, "work")
    os.makedirs(workdir, exist_ok=True)
    fl = os.path.join(workdir, "localtest_filelist.txt")
    with open(fl, "w") as fh:
        fh.write("\n".join(os.path.abspath(f) for f in files) + "\n")

    print("[local-test] {} local file(s): {}".format(len(files), ", ".join(files)))
    cmd = [
        sys.executable, MERGE_SCRIPT,
        "--flavor", args.flavor,
        "--filelist", fl,
        "--sample", args.local_sample,
        "--tag", args.local_tag,
        "--outdir", args.outdir,
        "--pt-threshold", str(args.pt_threshold),
        "--leptons-per-group", str(args.leptons_per_group),
        "--batch-id", "local",
    ]
    print("[local-test] " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=HERE).returncode


def write_submit_files(args, grouped, submit_dir, queue_dir, logs_root):
    submit_files = []
    # Stage the grid proxy inside the work dir (parent of submit_dir) so condor
    # can read it, and point every job at that copy.
    x509 = x509_block(os.path.join(os.path.dirname(submit_dir), "proxy"))
    for sample, sjobs in grouped.items():
        logdir = os.path.join(logs_root, sample)
        os.makedirs(logdir, exist_ok=True)
        queue_file = os.path.join(queue_dir, "queue_{}.txt".format(sample))
        with open(queue_file, "w") as fh:
            for j in sorted(sjobs, key=lambda x: int(x["batch_id"])):
                fh.write("{}, {}, {}, {}, {}\n".format(
                    j["sample"], j["tag"], j["batch_id"],
                    os.path.basename(j["filelist"]), j["filelist"]))
        sub = SUBMIT_TEMPLATE.format(
            run_job=RUN_JOB, merge_script=MERGE_SCRIPT, flavor=args.flavor,
            x509=x509,
            outdir=args.outdir, pt_threshold=args.pt_threshold,
            leptons_per_group=args.leptons_per_group,
            sample=sample, logdir=logdir, queue_file=queue_file,
            request_memory=args.request_memory, request_disk=args.request_disk,
            max_runtime=args.max_runtime,
        )
        sub_path = os.path.join(submit_dir, "{}.sub".format(sample))
        with open(sub_path, "w") as fh:
            fh.write(sub)
        submit_files.append(sub_path)
        print("[submit-file] {} ({} jobs)".format(sub_path, len(sjobs)))
    return submit_files


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--flavor", required=True, choices=["muon", "electron"])
    p.add_argument("--outdir", required=True, help="output base dir; 'root:' prefix triggers xrdcp writes")
    p.add_argument("--manifest", default=os.path.join(HERE, "work", "manifest.json"))
    p.add_argument("--sample", action="append", default=None, help="glob to filter samples (repeatable)")
    p.add_argument("--pt-threshold", type=float, default=35.0, dest="pt_threshold")
    p.add_argument("--leptons-per-group", type=int, default=100000, dest="leptons_per_group")
    p.add_argument("--request-memory", default="16384", dest="request_memory",
                   help="MB; merge_ntuples buffers full nested records, so give room")
    p.add_argument("--request-disk", default="4096000", dest="request_disk", help="KB")
    p.add_argument("--max-runtime", default="10800", dest="max_runtime", help="seconds")
    p.add_argument("--dry-run", action="store_true", dest="dry_run")
    p.add_argument("--submit-test", action="store_true", dest="submit_test",
                   help="submit only the first batch of the first matched sample (full condor round-trip)")
    # local-test (no condor, no xrdcp) options
    p.add_argument("--local-test", action="store_true", dest="local_test")
    p.add_argument("--local-input", default=None, dest="local_input",
                   help="local .root file, directory, or .txt filelist for --local-test")
    p.add_argument("--local-test-files", type=int, default=2, dest="local_test_files")
    p.add_argument("--local-sample", default="localtest", dest="local_sample",
                   help="sample label for --local-test output path")
    p.add_argument("--local-tag", default="localtest", dest="local_tag",
                   help="tag label for --local-test output path")
    args = p.parse_args()

    # local-test runs entirely on local files; no manifest / discovery needed.
    if args.local_test:
        return local_test(args)

    manifest = load_manifest(args.manifest)
    jobs = select(manifest, args.sample)
    if not jobs:
        print("[error] no jobs in manifest matched sample filter", file=sys.stderr)
        return 1

    if args.submit_test:
        job = sorted(jobs, key=lambda j: (j["sample"], int(j["batch_id"])))[0]
        jobs = [job]
        print("[submit-test] one condor job: sample={} batch={}".format(job["sample"], job["batch_id"]))

    workdir = os.path.dirname(os.path.abspath(args.manifest))
    submit_dir = os.path.join(workdir, "submit")
    queue_dir = os.path.join(workdir, "queue")
    logs_root = os.path.join(workdir, "logs")
    for d in (submit_dir, queue_dir, logs_root):
        os.makedirs(d, exist_ok=True)

    submit_files = write_submit_files(args, by_sample(jobs), submit_dir, queue_dir, logs_root)

    if not args.dry_run and shutil.which("condor_submit") is None:
        print(
            "[error] 'condor_submit' not found on this machine. HTCondor jobs must be "
            "submitted from an IIHE scheduler/submit node.\n"
            "        The submit file(s) were written; submit them there, e.g.:\n"
            + "\n".join("          condor_submit {}".format(s) for s in submit_files)
            + "\n        (or re-run with --dry-run to only generate the submit files).",
            file=sys.stderr,
        )
        return 1

    for sub_path in submit_files:
        cmd = ["condor_submit", sub_path]
        if args.dry_run:
            print("[dry-run] " + " ".join(cmd))
        else:
            subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
