#!/usr/bin/env python3
"""Merge lepton ntuples across many .root files and split them into parquet groups.

One entry of ``ntuplizer_<flavor>/Events`` is one lepton. This script reads a list
of input .root files (local paths or ``root://`` URLs), splits every lepton into a
(gen-flavor category x pT range) group and writes each group to ``.parquet`` in
shards of ``--leptons-per-group`` leptons.

It is written to run inside a single HTCondor job over a batch of files. To stay
memory-aware it processes one input file at a time (copying remote files to a local
tmp dir with ``xrdcp`` and deleting them right after reading), reads each tree in
entry batches, and dumps a group to disk as soon as it reaches the target size.

See ``README.md`` for the full workflow.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import awkward as ak
import numpy as np
import uproot

# gen-flavor category -> genPartFlav values that map to it. Anything not listed
# falls into "fake".
FLAVOR_CATEGORIES = {
    "prompt": (1,),
    "tau": (15,),
    "heavy": (5,),
    "light": (3, 4),
}
FAKE_CATEGORY = "fake"

# Fixed category ordering -> integer code. "fake" is the last index and the
# default (anything not matching a FLAVOR_CATEGORIES value). Used to turn the
# per-lepton category into an int code for fast, vectorized splitting.
ORDER = list(FLAVOR_CATEGORIES) + [FAKE_CATEGORY]
CAT_INDEX = {name: i for i, name in enumerate(ORDER)}


def is_remote(path):
    return path.startswith("root:")


def run(cmd):
    """Run a command, streaming output; raise on non-zero exit."""
    print("[cmd] " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def group_name(category, high_pt, pt_threshold):
    """Folder name encoding flavor category and pT range, e.g. ``prompt_ptGe35``."""
    thr = int(pt_threshold) if float(pt_threshold).is_integer() else pt_threshold
    side = "ptGe{}".format(thr) if high_pt else "ptLt{}".format(thr)
    return "{}_{}".format(category, side)


def all_group_names(pt_threshold):
    names = []
    for category in list(FLAVOR_CATEGORIES) + [FAKE_CATEGORY]:
        for high_pt in (True, False):
            names.append(group_name(category, high_pt, pt_threshold))
    return names


def category_codes(gen_part_flav):
    """Return an int8 category index per lepton (index into ``ORDER``).

    Defaults to the ``fake`` index; genPartFlav values listed in
    ``FLAVOR_CATEGORIES`` override it. Pure-numpy and vectorized (no object
    arrays / string comparisons).
    """
    flav = ak.to_numpy(gen_part_flav)
    codes = np.full(len(flav), CAT_INDEX[FAKE_CATEGORY], dtype=np.int8)
    for category, values in FLAVOR_CATEGORIES.items():
        codes[np.isin(flav, values)] = CAT_INDEX[category]
    return codes


class Accumulator:
    """Buffers leptons per group and flushes full shards to parquet."""

    def __init__(self, args):
        self.args = args
        self.chunks = {}  # group -> list of ak.Array
        self.counts = {}  # group -> int
        self.shard = {}   # group -> next shard index
        self.group_totals = {}  # group -> total leptons written (across all shards)
        self.buffered = 0  # total leptons currently held in self.chunks (all groups)
        self.written = 0

    def add(self, group, array):
        if len(array) == 0:
            return
        self.chunks.setdefault(group, []).append(array)
        self.counts[group] = self.counts.get(group, 0) + len(array)
        self.buffered += len(array)
        while self.counts[group] >= self.args.leptons_per_group:
            self._dump_full(group)
        self._enforce_cap()

    def _enforce_cap(self):
        """Bound total buffered leptons by flushing the largest group(s).

        The memory hogs are the high-population groups; flushing them keeps RAM
        bounded while low-population groups (tiny) stay buffered until flush().
        """
        while self.buffered > self.args.max_buffer:
            group = max(self.counts, key=self.counts.get)
            if self.counts[group] == 0:
                break
            if self.counts[group] >= self.args.leptons_per_group:
                self._dump_full(group)
            else:
                self._dump_partial(group)

    def _dump_full(self, group):
        n = self.args.leptons_per_group
        merged = ak.concatenate(self.chunks[group])
        self._write(group, merged[:n])
        self.buffered -= n
        remainder = merged[n:]
        if len(remainder) > 0:
            self.chunks[group] = [remainder]
            self.counts[group] = len(remainder)
        else:
            self.chunks[group] = []
            self.counts[group] = 0
        del merged

    def _dump_partial(self, group):
        """Write the whole (sub-target) group as one shard and clear it."""
        merged = ak.concatenate(self.chunks[group])
        self._write(group, merged)
        self.buffered -= len(merged)
        self.chunks[group] = []
        self.counts[group] = 0
        del merged

    def flush(self):
        """Write out all remaining (partial) shards."""
        for group in list(self.chunks):
            if self.counts.get(group, 0) > 0:
                merged = ak.concatenate(self.chunks[group])
                self._write(group, merged)
            self.chunks[group] = []
            self.counts[group] = 0
        self.buffered = 0

    def _write(self, group, array):
        idx = self.shard.get(group, 0)
        self.shard[group] = idx + 1
        fname = "{}_{}_batch{}_shard{}.parquet".format(
            self.args.flavor, self.args.sample, self.args.batch_id, idx
        )
        scratch = os.path.join(self.args.tmpdir, fname)
        ak.to_parquet(array, scratch)
        dest_dir = "/".join([self.args.outdir, self.args.sample, self.args.tag, group])
        self._deliver(scratch, dest_dir, fname)
        self.group_totals[group] = self.group_totals.get(group, 0) + len(array)
        self.written += len(array)
        print(
            "[dump] {} -> {}/{} ({} leptons)".format(group, dest_dir, fname, len(array)),
            flush=True,
        )

    def _deliver(self, scratch, dest_dir, fname):
        if is_remote(self.args.outdir):
            dest = dest_dir + "/" + fname
            # -p creates the remote destination directory tree; -f overwrites.
            run(["xrdcp", "-f", "-p", scratch, dest])
            os.remove(scratch)
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(scratch, os.path.join(dest_dir, fname))

    def write_summary(self):
        """Write one per-job JSON with the lepton count in every category group.

        Stored in a ``summary`` folder alongside the group folders, i.e.
        ``<outdir>/<sample>/<tag>/summary/<flavor>_<sample>_batch<b>.json``.
        Every group is listed (0 when the job produced none) so the counts are
        unambiguous when combined across jobs.
        """
        groups = {name: 0 for name in all_group_names(self.args.pt_threshold)}
        groups.update(self.group_totals)
        summary = {
            "flavor": self.args.flavor,
            "sample": self.args.sample,
            "tag": self.args.tag,
            "batch_id": self.args.batch_id,
            "pt_threshold": self.args.pt_threshold,
            "total_leptons": self.written,
            "groups": dict(sorted(groups.items())),
        }
        fname = "{}_{}_batch{}.json".format(
            self.args.flavor, self.args.sample, self.args.batch_id
        )
        scratch = os.path.join(self.args.tmpdir, fname)
        with open(scratch, "w") as fh:
            json.dump(summary, fh, indent=2)
        dest_dir = "/".join([self.args.outdir, self.args.sample, self.args.tag, "summary"])
        self._deliver(scratch, dest_dir, fname)
        print("[summary] {} leptons across {} groups -> {}/{}".format(
            self.written, len(self.group_totals), dest_dir, fname), flush=True)


class Prefetcher:
    """One-deep xrdcp prefetch: download file N+1 while file N is processed.

    ``get(i)`` ensures file ``i`` is available locally, kicks off the download of
    ``i+1`` in the background, and returns ``(local_path, copied)``. Local (non
    ``root://``) inputs are a passthrough. At most two remote files are on disk
    at once (delete the current one after reading — see the main loop).
    """

    def __init__(self, urls, tmpdir):
        self.urls = urls
        self.tmpdir = tmpdir
        self.inflight = {}  # index -> (local_path, Popen|None, copied)

    def _start(self, i):
        if i < 0 or i >= len(self.urls) or i in self.inflight:
            return
        url = self.urls[i]
        if not is_remote(url):
            self.inflight[i] = (url, None, False)
            return
        local = os.path.join(self.tmpdir, os.path.basename(url))
        print("[prefetch] xrdcp -f {} {}".format(url, local), flush=True)
        proc = subprocess.Popen(["xrdcp", "-f", url, local])
        self.inflight[i] = (local, proc, True)

    def get(self, i):
        self._start(i)
        self._start(i + 1)  # overlap next download with this file's compute
        local, proc, copied = self.inflight[i]
        if proc is not None:
            rc = proc.wait()
            if rc != 0:
                raise subprocess.CalledProcessError(rc, ["xrdcp", "-f", self.urls[i], local])
        return local, copied

    def done(self, i):
        self.inflight.pop(i, None)


def process_file(local, args, tree_name, acc):
    # code -> group folder: high_pt is the even code, low_pt the odd one.
    group_by_code = [group_name(ORDER[c // 2], (c % 2 == 0), args.pt_threshold)
                     for c in range(2 * len(ORDER))]
    with uproot.open(local) as f:
        if tree_name not in f:
            print("[warn] {} missing in {}, skipping".format(tree_name, local), flush=True)
            return
        tree = f[tree_name]
        for chunk in tree.iterate(step_size=args.read_step, library="ak"):
            high = ak.to_numpy(chunk["Lepton_pt"]) >= args.pt_threshold
            gcode = (category_codes(chunk["genPartFlav"]).astype(np.int64) * 2
                     + np.where(high, 0, 1))
            # One stable gather groups all leptons by code, preserving intra-group
            # order, so a single full-record materialization replaces up to 10
            # boolean-index copies.
            order = np.argsort(gcode, kind="stable")
            sorted_chunk = chunk[ak.Array(order)]
            del chunk
            counts = np.bincount(gcode, minlength=len(group_by_code))
            ends = np.cumsum(counts)
            starts = ends - counts
            for c in range(len(group_by_code)):
                n = int(counts[c])
                if n == 0:
                    continue
                # ak.to_packed is REQUIRED: a bare slice is a view that would pin
                # the whole sorted_chunk buffer alive via a tiny sub-slice.
                sub = ak.to_packed(sorted_chunk[int(starts[c]):int(ends[c])])
                acc.add(group_by_code[c], sub)
            del sorted_chunk


def read_filelist(path):
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--flavor", required=True, choices=["muon", "electron"])
    p.add_argument("--filelist", required=True, help="text file, one input .root path/URL per line")
    p.add_argument("--sample", required=True)
    p.add_argument("--tag", required=True, help="production-tag folder (first dir after sample name)")
    p.add_argument("--outdir", required=True, help="output base dir; if it starts with 'root:' xrdcp is used")
    p.add_argument("--pt-threshold", type=float, default=35.0, dest="pt_threshold")
    p.add_argument("--leptons-per-group", type=int, default=100000, dest="leptons_per_group")
    p.add_argument("--max-buffer", type=int, default=1500000, dest="max_buffer",
                   help="cap on total leptons buffered across all groups before the "
                        "largest group is flushed (bounds RAM)")
    p.add_argument("--batch-id", default="0", dest="batch_id")
    p.add_argument("--read-step", type=int, default=100000, dest="read_step",
                   help="uproot entry-batch size for reading each tree")
    p.add_argument("--tmpdir", default=None, help="scratch dir for xrdcp/parquet (default: $TMPDIR or /tmp)")
    p.add_argument("--max-files", type=int, default=None, dest="max_files",
                   help="only process the first N files (local testing)")
    args = p.parse_args()

    if args.tmpdir is None:
        args.tmpdir = os.environ.get("TMPDIR") or os.environ.get("_CONDOR_SCRATCH_DIR") or "/tmp"
    os.makedirs(args.tmpdir, exist_ok=True)

    tree_name = "ntuplizer_{}/Events".format(args.flavor)
    files = read_filelist(args.filelist)
    if args.max_files is not None:
        files = files[: args.max_files]

    print("[info] flavor={} sample={} tag={} tree={}".format(
        args.flavor, args.sample, args.tag, tree_name), flush=True)
    print("[info] {} input files, outdir={}, tmpdir={}".format(
        len(files), args.outdir, args.tmpdir), flush=True)

    acc = Accumulator(args)
    prefetch = Prefetcher(files, args.tmpdir)
    for i, url in enumerate(files):
        print("[file {}/{}] {}".format(i + 1, len(files), url), flush=True)
        local, copied = prefetch.get(i)
        try:
            process_file(local, args, tree_name, acc)
        finally:
            if copied and os.path.exists(local):
                os.remove(local)
            prefetch.done(i)
    acc.flush()
    acc.write_summary()

    print("[done] wrote {} leptons across {} groups".format(acc.written, len(acc.shard)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
