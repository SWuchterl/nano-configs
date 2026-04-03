#!/usr/bin/env python3
"""Merge keep/drop txt files for CMSSW and produce a merged.txt plus a CSV report.

Usage: python merge.py [--dir DIR] [--out MERGED_TXT] [--report MERGED_CSV]

Behavior:
- Reads all .txt files in the directory (excluding the outputs), parses lines
  that start with 'keep' or 'drop'.
- Builds a per-file mapping variable -> action (keep/drop).
- Merges decisions for each variable: if any file requests 'keep', final is 'keep', else 'drop'.
- Writes `merged.txt` with the merged keep/drop lines and a CSV report table.
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List


def natural_key(s: str):
    """Key for natural (human) sorting: split numbers, case-insensitive."""
    parts = re.split(r"(\d+)", s)
    key = []
    for p in parts:
        if p.isdigit():
            key.append(int(p))
        else:
            key.append(p.lower())
    return key


def parse_keepdrop_file(path: str) -> Dict[str, str]:
    """Parse a single txt file and return mapping variable->action ('keep'/'drop').

    Lines beginning with '#' or empty lines are ignored. Only lines starting
    with 'keep' or 'drop' (case-insensitive) are considered. The rest of the
    line after the first token is used as the variable/pattern key.
    """
    mapping: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            # remove inline comments starting with '#' or '//' (keep content before them)
            line = raw.rstrip("\n")
            i_hash = line.find('#')
            i_slash = line.find('//')
            cut = None
            if i_hash != -1:
                cut = i_hash
            if i_slash != -1 and (cut is None or i_slash < cut):
                cut = i_slash
            if cut is not None:
                line = line[:cut]

            line = line.strip()
            if not line:
                continue

            parts = line.split(None, 1)
            if not parts:
                continue

            action = parts[0].lower()
            # accept variants like 'dropmatch' by treating any action that
            # starts with 'drop' as 'drop', and similarly for 'keep'
            if action.startswith("keep"):
                action_val = "keep"
            elif action.startswith("dropmatch"):
                action_val = "dropmatch"
            elif action.startswith("drop"):
                action_val = "drop"
            else:
                continue

            if len(parts) == 1:
                # no variable specified -> skip
                continue
            key = parts[1].strip()
            if not key:
                continue
            mapping[key] = action_val
    return mapping


def find_txt_files(directory: str, exclude: List[str]) -> List[str]:
    files = sorted(glob.glob(os.path.join(directory, "*.txt")))
    return [f for f in files if os.path.basename(f) not in exclude]


def merge_mappings(per_file: Dict[str, Dict[str, str]]):
    """Merge mappings and return (merged_dict, rows, conflict_count).

    - merged_dict: variable -> merged action
    - rows: list of (variable, {file: action}, merged_action) for reporting
    - conflict_count: number of variables where both keep and drop appear across files
    """
    all_keys = set()
    for m in per_file.values():
        all_keys.update(m.keys())

    merged: Dict[str, str] = {}
    rows = []
    conflict_count = 0

    files = sorted(per_file.keys())

    for key in sorted(all_keys, key=natural_key):
        actions = {f: per_file[f].get(key) for f in files}
        action_values = [a for a in actions.values() if a is not None]

        has_keep = any(a.startswith("keep") for a in action_values)
        has_drop = any(a.startswith("drop") for a in action_values)

        if has_keep:
            merged_action = "keep"
        elif has_drop:
            # Prefer 'dropmatch' if present, then 'drop', else pick a deterministic drop-variant
            if any(a == "dropmatch" for a in action_values):
                merged_action = "dropmatch"
            elif any(a == "drop" for a in action_values):
                merged_action = "drop"
            else:
                # fallback: choose the first sorted drop-like variant
                drops = sorted([a for a in action_values if a.startswith("drop")])
                merged_action = drops[0] if drops else "drop"
        else:
            # no explicit action found; default to drop
            merged_action = "drop"

        if has_keep and has_drop:
            conflict_count += 1

        merged[key] = merged_action
        rows.append((key, actions, merged_action))

    return merged, rows, conflict_count


def write_merged_txt(path: str, merged: Dict[str, str]):
    with open(path, "w", encoding="utf-8") as f:
        for key in sorted(merged.keys(), key=natural_key):
            f.write(f"{merged[key]} {key}\n")


def write_report_csv(path: str, rows, files: List[str]):
    header = ["variable"] + files + ["merged"]
    with open(path, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(header)
        for key, actions, merged_action in sorted(rows, key=lambda r: natural_key(r[0])):
            row = [key]
            for f in files:
                row.append(actions.get(f, ""))
            row.append(merged_action)
            writer.writerow(row)


def print_summary(total_vars: int, conflict_count: int, out_txt: str, out_csv: str):
    print(f"Wrote merged file: {out_txt}")
    print(f"Wrote report CSV: {out_csv}")
    print(f"Variables processed: {total_vars}")
    print(f"Conflicts (keep vs drop): {conflict_count}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Merge keep/drop .txt files for CMSSW")
    parser.add_argument("--dir", default=".", help="Directory with .txt files (default: .)")
    parser.add_argument("--out", default="keep_and_drop.txt", help="Output merged txt file name")
    parser.add_argument("--report", default="merged_table.csv", help="Output CSV report name")
    args = parser.parse_args(argv)

    directory = os.path.abspath(args.dir)
    out_txt = os.path.join(directory, args.out)
    out_csv = os.path.join(directory, args.report)

    exclude = [os.path.basename(out_txt), os.path.basename(out_csv)]
    files = find_txt_files(directory, exclude)
    if not files:
        print(f"No .txt files found in {directory}")
        return 1

    per_file: Dict[str, Dict[str, str]] = {}
    for fpath in files:
        fname = os.path.basename(fpath)
        per_file[fname] = parse_keepdrop_file(fpath)

    merged, rows, conflict_count = merge_mappings(per_file)

    write_merged_txt(out_txt, merged)
    write_report_csv(out_csv, rows, sorted(per_file.keys()))
    print_summary(len(rows), conflict_count, out_txt, out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
