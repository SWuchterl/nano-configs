#!/usr/bin/env python3
"""Discover input samples/files and prepare HTCondor batch filelists.

Lists every ``tree_*.root`` file under each sample directory of an input base
(default the 2018UL ParT samples on /pnfs at IIHE), derives the production-tag
folder (the first directory after the sample name), splits each sample's files
into batches of ``--files-per-batch`` and writes:

  <workdir>/filelists/<sample>/batch_<i>.txt   one root:// URL per line
  <workdir>/manifest.json                       [{sample, tag, batch_id, filelist}, ...]

Run this on the submit node before ``submit_condor.py``.
"""
import argparse
import fnmatch
import json
import os
import subprocess
import sys

DEFAULT_REDIRECTOR = "root://maite.iihe.ac.be"
DEFAULT_INPUT_BASE = "/pnfs/iihe/cms/store/group/CustomNanoAODv15/ParTSamples2018UL/2018/mc"


def xrdfs_host(redirector):
    return redirector.replace("root://", "").rstrip("/")


def list_dir(redirector, path):
    """Return entries directly under ``path`` (absolute pnfs paths)."""
    out = subprocess.run(
        ["xrdfs", xrdfs_host(redirector), "ls", path],
        check=True, capture_output=True, text=True,
    ).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def list_root_files(redirector, path):
    """Recursively return all ``tree_*.root`` files under ``path``."""
    out = subprocess.run(
        ["xrdfs", xrdfs_host(redirector), "ls", "-R", path],
        check=True, capture_output=True, text=True,
    ).stdout
    return [
        line.strip()
        for line in out.splitlines()
        if line.strip().endswith(".root") and os.path.basename(line.strip()).startswith("tree_")
    ]


def chunk(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--redirector", default=DEFAULT_REDIRECTOR)
    p.add_argument("--input-base", default=DEFAULT_INPUT_BASE, dest="input_base",
                   help="pnfs directory that holds one subdir per sample")
    p.add_argument("--sample", action="append", default=None,
                   help="glob to select samples (repeatable); default: all")
    p.add_argument("--files-per-batch", type=int, default=100, dest="files_per_batch")
    p.add_argument("--workdir", default=os.path.join(os.path.dirname(__file__), "work"))
    args = p.parse_args()

    filelist_root = os.path.join(args.workdir, "filelists")
    os.makedirs(filelist_root, exist_ok=True)

    sample_paths = list_dir(args.redirector, args.input_base)
    samples = sorted(os.path.basename(sp) for sp in sample_paths)
    if args.sample:
        samples = [s for s in samples if any(fnmatch.fnmatch(s, pat) for pat in args.sample)]
    if not samples:
        print("[error] no samples matched", file=sys.stderr)
        return 1

    manifest = []
    for sample in samples:
        sample_dir = args.input_base + "/" + sample
        files = sorted(list_root_files(args.redirector, sample_dir))
        if not files:
            print("[warn] no tree_*.root under {}".format(sample), file=sys.stderr)
            continue
        # <TAG> = first path component after the sample name.
        rel = files[0][len(sample_dir) + 1:]
        tag = rel.split("/", 1)[0]

        urls = [args.redirector + f for f in files]
        sample_fl_dir = os.path.join(filelist_root, sample)
        os.makedirs(sample_fl_dir, exist_ok=True)
        for i, batch in enumerate(chunk(urls, args.files_per_batch)):
            fl = os.path.join(sample_fl_dir, "batch_{}.txt".format(i))
            with open(fl, "w") as fh:
                fh.write("\n".join(batch) + "\n")
            manifest.append({"sample": sample, "tag": tag, "batch_id": str(i), "filelist": fl})
        print("[ok] {}: {} files -> {} batches (tag={})".format(
            sample, len(urls), (len(urls) + args.files_per_batch - 1) // args.files_per_batch, tag))

    manifest_path = os.path.join(args.workdir, "manifest.json")
    with open(manifest_path, "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("[done] {} jobs across {} samples -> {}".format(len(manifest), len(samples), manifest_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
