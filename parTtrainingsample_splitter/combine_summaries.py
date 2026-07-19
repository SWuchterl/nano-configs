#!/usr/bin/env python3
"""Combine the per-job summary JSONs into one total view of the training leptons.

Each merge job writes ``<outdir>/<sample>/<tag>/summary/<flavor>_<sample>_batch<b>.json``
holding the lepton count in every category group for that job (see
``merge_ntuples.py``). This script walks an output tree, reads every such summary
and aggregates the counts across **all jobs and all samples**, so you get the
total number of leptons available to train on, broken down by group, flavor and
sample.

The input tree may be a local path or a remote ``root://`` URL (the same value
passed as ``--outdir`` to ``submit_condor.py``); remote trees are listed with
``xrdfs`` and each summary fetched with ``xrdcp``.

Writes the combined view to ``--output`` (default ``combined_summary.json`` in the
current dir) and prints a readable table.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

DEFAULT_REDIRECTOR = "root://maite.iihe.ac.be"


def is_remote(path):
    return path.startswith("root:")


def split_remote(url):
    """Split a ``root://host//abs/path`` URL into (redirector, absolute path)."""
    body = url[len("root://"):]
    host, _, path = body.partition("/")
    return "root://" + host, "/" + path


def xrdfs_host(redirector):
    return redirector.replace("root://", "").rstrip("/")


def find_summaries_local(indir):
    """Return local paths of every ``summary/*.json`` under ``indir``."""
    found = []
    for root, _dirs, files in os.walk(indir):
        if os.path.basename(root) != "summary":
            continue
        for f in files:
            if f.endswith(".json"):
                found.append(os.path.join(root, f))
    return sorted(found)


def find_summaries_remote(indir):
    """Return ``root://`` URLs of every ``summary/*.json`` under a remote tree."""
    redirector, base = split_remote(indir)
    out = subprocess.run(
        ["xrdfs", xrdfs_host(redirector), "ls", "-R", base],
        check=True, capture_output=True, text=True,
    ).stdout
    urls = []
    for line in out.splitlines():
        p = line.strip()
        if p.endswith(".json") and "/summary/" in p:
            urls.append(redirector + p)
    return sorted(urls)


def load_summary_local(path):
    with open(path) as fh:
        return json.load(fh)


def load_summary_remote(url, tmpdir):
    dest = os.path.join(tmpdir, os.path.basename(url))
    subprocess.run(["xrdcp", "-f", url, dest], check=True,
                   capture_output=True, text=True)
    with open(dest) as fh:
        data = json.load(fh)
    os.remove(dest)
    return data


def add_groups(dst, groups):
    for g, n in groups.items():
        dst[g] = dst.get(g, 0) + n


def combine(summaries):
    """Aggregate a list of per-job summary dicts into one combined view."""
    total = 0
    by_group = {}
    by_flavor = {}
    by_sample = {}
    samples = set()
    flavors = set()

    for s in summaries:
        flavor = s.get("flavor", "unknown")
        sample = s.get("sample", "unknown")
        groups = s.get("groups", {})
        n_total = s.get("total_leptons", sum(groups.values()))
        samples.add(sample)
        flavors.add(flavor)

        total += n_total
        add_groups(by_group, groups)

        fl = by_flavor.setdefault(flavor, {"total_leptons": 0, "by_group": {}})
        fl["total_leptons"] += n_total
        add_groups(fl["by_group"], groups)

        sm = by_sample.setdefault(
            sample, {"total_leptons": 0, "by_flavor": {}})
        sm["total_leptons"] += n_total
        smf = sm["by_flavor"].setdefault(
            flavor, {"total_leptons": 0, "by_group": {}})
        smf["total_leptons"] += n_total
        add_groups(smf["by_group"], groups)

    def sort_groups(d):
        d["by_group"] = dict(sorted(d["by_group"].items()))

    for fl in by_flavor.values():
        sort_groups(fl)
    for sm in by_sample.values():
        for smf in sm["by_flavor"].values():
            sort_groups(smf)

    return {
        "n_summary_files": len(summaries),
        "samples": sorted(samples),
        "flavors": sorted(flavors),
        "total_leptons": total,
        "by_group": dict(sorted(by_group.items())),
        "by_flavor": {k: by_flavor[k] for k in sorted(by_flavor)},
        "by_sample": {k: by_sample[k] for k in sorted(by_sample)},
    }


def print_table(combined):
    print("=" * 60)
    print("combined lepton counts  ({} summary files, {} samples)".format(
        combined["n_summary_files"], len(combined["samples"])))
    print("=" * 60)

    print("\nby group (all samples, all flavors):")
    for g, n in combined["by_group"].items():
        print("  {:<20} {:>12,}".format(g, n))

    print("\nby flavor:")
    for flavor, fl in combined["by_flavor"].items():
        print("  {:<20} {:>12,}".format(flavor, fl["total_leptons"]))

    print("\nby sample:")
    for sample, sm in combined["by_sample"].items():
        flav = ", ".join("{}={:,}".format(f, v["total_leptons"])
                         for f, v in sm["by_flavor"].items())
        print("  {:<40} {:>12,}   [{}]".format(sample, sm["total_leptons"], flav))

    print("\n{:<20} {:>12,}".format("TOTAL leptons", combined["total_leptons"]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("indir", help="output tree root: local path or root:// URL "
                                  "(same value used as submit_condor.py --outdir)")
    p.add_argument("--output", default="combined_summary.json",
                   help="where to write the combined JSON (default: ./combined_summary.json)")
    args = p.parse_args()

    if is_remote(args.indir):
        urls = find_summaries_remote(args.indir)
        if not urls:
            print("[error] no summary/*.json found under {}".format(args.indir), file=sys.stderr)
            return 1
        with tempfile.TemporaryDirectory() as tmp:
            summaries = [load_summary_remote(u, tmp) for u in urls]
    else:
        paths = find_summaries_local(args.indir)
        if not paths:
            print("[error] no summary/*.json found under {}".format(args.indir), file=sys.stderr)
            return 1
        summaries = [load_summary_local(pth) for pth in paths]

    combined = combine(summaries)
    with open(args.output, "w") as fh:
        json.dump(combined, fh, indent=2)

    print_table(combined)
    print("\n[done] combined {} summaries -> {}".format(
        combined["n_summary_files"], args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
