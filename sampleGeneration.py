#!/usr/bin/env python3
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


SPREADSHEET_URLS = {
    "2025": (
        "http://docs.google.com/spreadsheets/d/"
        "1LrKEphbzf0Ndt72WLrTjCrIh3_tuOEcQuTPHvCjlpQE/"
        "export?format=csv&gid=645761148"
    ),
    "2024": (
        "http://docs.google.com/spreadsheets/d/"
        "1LrKEphbzf0Ndt72WLrTjCrIh3_tuOEcQuTPHvCjlpQE/"
        "export?format=csv&gid=891834841"
    ),
    "2023": (
        "http://docs.google.com/spreadsheets/d/"
        "1LrKEphbzf0Ndt72WLrTjCrIh3_tuOEcQuTPHvCjlpQE/"
        "export?format=csv&gid=723442297"
    ),
    "2022": (
        "http://docs.google.com/spreadsheets/d/"
        "1LrKEphbzf0Ndt72WLrTjCrIh3_tuOEcQuTPHvCjlpQE/"
        "export?format=csv&gid=837854228"
    ),
    "2018": (
        "http://docs.google.com/spreadsheets/d/"
        "1LrKEphbzf0Ndt72WLrTjCrIh3_tuOEcQuTPHvCjlpQE/"
        "export?format=csv&gid=1486209551"
    )
}


def normalize(text):
    return (text or "").strip()


def find_header_and_indices(rows):
    needed = {"miniaod", "nanoaod", "assignment", "type", "status", "events"}
    for i, row in enumerate(rows):
        lowered = [normalize(c).lower() for c in row]
        if not needed.issubset(set(lowered)):
            continue
        return i, {
            "miniaod": lowered.index("miniaod"),
            "nanoaod": lowered.index("nanoaod"),
            "assignment": lowered.index("assignment"),
            "type": lowered.index("type"),
            "status": lowered.index("status"),
            "events": lowered.index("events"),
            "sample": lowered.index("sample") if "sample" in lowered else None,
        }
    raise ValueError(
        "Could not find CSV header with MiniAOD, NanoAOD, Assignment, "
        "Type, Status, and Events columns"
    )


def parse_int_value(value):
    text = normalize(value).replace(",", "")
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_spreadsheet(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header_idx, col = find_header_and_indices(rows)
    entries = []
    max_idx = max(v for v in col.values() if v is not None)

    for row_idx, row in enumerate(rows[header_idx + 1:],
                                  start=header_idx + 2):
        if not row:
            continue
        if len(row) <= max_idx:
            continue

        miniaod = normalize(row[col["miniaod"]])
        nanoaod = normalize(row[col["nanoaod"]])
        assignment = normalize(row[col["assignment"]])
        status = normalize(row[col["status"]])
        sample_type = normalize(row[col["type"]])
        events = parse_int_value(row[col["events"]])

        if not nanoaod and not miniaod:
            continue

        sample = (
            normalize(row[col["sample"]]) if col["sample"] is not None else ""
        )

        entries.append(
            {
                "row": row_idx,
                "sample": sample,
                "miniaod": miniaod,
                "nanoaod": nanoaod,
                "assignment": assignment,
                "status": status,
                "type": sample_type,
                "events": events,
            }
        )

    return entries


def extract_dataset_name(miniaod):
    parts = normalize(miniaod).split("/")
    if len(parts) > 2 and parts[1]:
        return parts[1]
    return ""


def extract_campaign_name(miniaod):
    parts = normalize(miniaod).split("/")
    if len(parts) > 2 and parts[2]:
        return parts[2]
    return ""


PROGRESS_LISTING_QUERY = (
    "dataset=/*/*NanoTuples*parTlepID*/USER instance=prod/phys03"
)
PUBLISHED_VERNAME_RE = re.compile(r"NanoAODv15_(.+)-[0-9a-f]{32}$")
COMPLETE_FRACTION = 0.999


def crab_vername(miniaod):
    # Same as the vername in crab.py:parseDatasetName (which can't be
    # imported here because crab.py needs CRABClient). The output dataset
    # tag is "<tag>_<vername>", so this is what the NanoAOD name ends with.
    parts = normalize(miniaod)[1:].split("/")
    if len(parts) != 3:
        return ""
    ver = parts[1]
    if re.match(r"Run20[0-9][0-9][A-Z]-", ver):
        return ver
    ver_pieces = ver.split("_")
    keep_idx = 1
    for idx, s in enumerate(ver_pieces):
        if s.startswith("mc"):
            keep_idx = idx
            break
    rlt = re.search(r"_(v[0-9]+)(_ext[0-9]+|)(_L1v[0-9]+|)(-v[0-9]+)", ver)
    if rlt:
        rlt = rlt.groups()
        ext = "_" + rlt[0] + rlt[1].replace("_", "-") + rlt[-1]
    else:
        ext = ""
    return "_".join(ver_pieces[:keep_idx]) + ext


def list_published_datasets():
    rc, lines, err = run_dasgoclient_query(PROGRESS_LISTING_QUERY)
    if rc != 0:
        raise RuntimeError(f"DAS listing failed: {err}")

    index = {}
    for name in lines:
        parts = name[1:].split("/")
        if len(parts) != 3:
            continue
        match = PUBLISHED_VERNAME_RE.search(parts[1])
        if not match:
            continue
        index.setdefault((parts[0], match.group(1)), []).append(name)
    return index


def select_candidates(entry, matches):
    is_muon_pog = "muonpog" in entry.get("sample", "").lower()
    candidates = [
        d for d in matches
        if ("NanoTuplesMuonPOG" in d.split("/")[2]) == is_muon_pog
    ]
    group = [
        d for d in candidates
        if d.split("/")[2].startswith("CustomNanoAODv15-")
    ]
    return group or candidates


def query_dataset_events(dataset):
    query = f"summary dataset={dataset}"
    if dataset.endswith("/USER"):
        query += " instance=prod/phys03"
    rc, lines, err = run_dasgoclient_query(query)
    if rc != 0:
        return None
    try:
        summary = json.loads("\n".join(lines))
    except json.JSONDecodeError:
        return None
    if not summary:
        return 0
    return summary[0].get("num_event", 0) or 0


def progress_status(expected, found):
    if found is None:
        return "DAS_ERROR"
    if not expected:
        return "FOUND"
    if found > expected:
        return "OVER"
    if found >= COMPLETE_FRACTION * expected:
        return "COMPLETE"
    return "PARTIAL"


def print_progress_bar(current, total, width=30):
    if total <= 0:
        return

    fraction = current / total
    filled = int(width * fraction)
    bar = "#" * filled + "-" * (width - filled)
    percent = fraction * 100.0
    sys.stdout.write(f"\r[{bar}] {current}/{total} ({percent:5.1f}%)")
    sys.stdout.flush()


def parse_assignment_list(value):
    if not value:
        return []
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def assignment_matches(entry_assignment, requested_user):
    if not requested_user:
        return True
    requested = requested_user.strip().lower()
    tokens = parse_assignment_list(entry_assignment)
    return requested in tokens


def write_split_confs(entries, year, requested_user=None):
    mc_path = Path("mc") / f"mc_{year}.conf"
    data_path = Path("data") / f"data_{year}.conf"
    mc_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.parent.mkdir(parents=True, exist_ok=True)

    mc_selected = []
    mc_commented_out = []
    data_selected = []
    data_commented_out = []
    seen_mc = set()
    seen_data = set()

    for e in entries:
        if requested_user and not assignment_matches(
            e["assignment"], requested_user
        ):
            continue

        sample_type = normalize(e.get("type")).lower()
        dataset = e["miniaod"]

        if dataset and dataset.endswith("/USER"):
            continue

        if sample_type == "data":
            if not dataset or not dataset.startswith("/"):
                continue
            if dataset in seen_data:
                continue
            seen_data.add(dataset)
            data_selected.append(dataset)
            continue

        if not dataset or not dataset.startswith("/"):
            continue
        if dataset in seen_mc:
            continue

        if not (e.get("status").lower() == "not started"):
            if sample_type == "data":
                data_commented_out.append(dataset)
            else:
                mc_commented_out.append(dataset)

        seen_mc.add(dataset)
        mc_selected.append(dataset)

    with open(mc_path, "w", encoding="utf-8") as mc_out:
        for dataset in mc_selected:
            if dataset in mc_commented_out:
                mc_out.write("# " + dataset + "\n")
            else:
                mc_out.write(dataset + "\n")

    with open(data_path, "w", encoding="utf-8") as data_out:
        for dataset in data_selected:
            if dataset in data_commented_out:
                data_out.write("# " + dataset + "\n")
            else:
                data_out.write(dataset + "\n")

    return mc_path, data_path, mc_selected, data_selected


def download_spreadsheet(year, csv_path):
    url = SPREADSHEET_URLS.get(str(year))
    if not url:
        supported = ", ".join(sorted(SPREADSHEET_URLS.keys()))
        raise ValueError(
            f"No spreadsheet configured for year '{year}'. "
            f"Supported years: {supported}"
        )

    cmd = ["curl", "-L", "-sS", url, "-o", str(csv_path)]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "Failed to download spreadsheet.csv: "
            f"{completed.stderr.strip() or 'curl returned non-zero exit code'}"
        )


def run_dasgoclient_query(query):
    cmd = ["dasgoclient", "--query", query]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    stdout_lines = [line.strip()
                    for line in completed.stdout.splitlines() if line.strip()]
    stderr = completed.stderr.strip()
    return completed.returncode, stdout_lines, stderr


def suggest_from_nano(nano_dataset):
    if not nano_dataset:
        return ""
    guess = nano_dataset.replace("/NANOAODSIM", "/MINIAODSIM")
    guess = guess.replace("/NANOAOD", "/MINIAOD")
    guess = guess.replace("NanoAOD", "MiniAOD")
    return guess


def validate_datasets(entries, requested_user=None):
    issues = []
    total = 0

    # check for duplicates in MiniAOD column
    seen_mini = set()

    for e in entries:
        nano = e["nanoaod"]
        expected_parent = e["miniaod"]
        sample_type = normalize(e.get("type"))

        if not expected_parent or not expected_parent.startswith("/"):
            continue

        if expected_parent in seen_mini:
            issues.append(
                {
                    "type": "duplicate_miniaod",
                    "miniaod": expected_parent,
                    "details": "Duplicate MiniAOD dataset found"
                }
            )
            print(f"  -> DUPLICATE MiniAOD: {expected_parent}")
            continue

        seen_mini.add(expected_parent)

        if requested_user and not assignment_matches(
            e["assignment"], requested_user
        ):
            continue

        total += 1
        print(f"[CHECK] {expected_parent}")

        rc_ds, ds_out, ds_err = run_dasgoclient_query(
            f"dataset={expected_parent}")
        exists = (rc_ds == 0 and expected_parent in ds_out)

        if not exists:
            issues.append(
                {
                    "type": "missing_miniaod",
                    "miniaod": expected_parent,
                    "nanoaod": nano,
                    "details": ds_err or "dataset not found in DAS output",
                }
            )
            print("  -> MiniAOD dataset not found in DAS")
            continue

        if expected_parent.endswith("/USER"):
            continue

        rc_parent, parent_out, parent_err = run_dasgoclient_query(
            f"parent dataset={nano}")
        parents = [p for p in parent_out if p.startswith("/")]

        if not nano:
            details = (
                "NanoAOD column is empty"
            )
            issues.append(
                {
                    "type": "missing_nanoaod",
                    "miniaod": expected_parent,
                    "details": details,
                }
            )
            print(f"  -> WARNING: {details}")
            continue

        elif rc_parent != 0 or not parents:
            issues.append(
                {
                    "type": "missing_parent",
                    "nanoaod": nano,
                    "expected_miniaod": expected_parent,
                    "found_parents": parents,
                    "suggested_miniaod": suggest_from_nano(nano),
                    "details": (
                        parent_err or "no parent dataset returned by DAS"
                    ),
                }
            )
            print("  -> MISSING parent MiniAOD in DAS")
            continue

        if sample_type.lower() == "data":
            continue

        if expected_parent not in parents:
            issues.append(
                {
                    "type": "parent_mismatch",
                    "nanoaod": nano,
                    "expected_miniaod": expected_parent,
                    "found_parents": parents,
                    "suggested_miniaod": parents[0],
                    "details": "parent dataset does not match MiniAOD column",
                }
            )
            print("  -> Parent mismatch")

    return total, issues


def default_progress_dataset_name(miniaod):
    # Name the CustomNanoAODv15 group would publish under, written for
    # samples that are not in DAS yet
    vername = crab_vername(miniaod)
    if not extract_dataset_name(miniaod) or not vername:
        return ""
    return (
        f"/{extract_dataset_name(miniaod)}/"
        "CustomNanoAODv15-NanoTuples-uParTv3-parTlepID-"
        f"NanoAODv15_{vername}-"
        "00000000000000000000000000000000/USER"
    )


def format_progress_line(user, dataset_name, miniaod, new_dataset_name,
                         expected_events, found_events):
    # Format the spreadsheet is updated from: keep it unchanged
    return (
        f"{user} {dataset_name} {miniaod} {new_dataset_name} "
        f"{expected_events} {found_events}"
    )


def run_progress_check(entries, year, requested_user=None, limit=None,
                       workers=8):
    samples = [entry for entry in entries if entry.get("miniaod")]
    if requested_user:
        samples = [
            e for e in samples
            if assignment_matches(e["assignment"], requested_user)
        ]
    if limit:
        samples = samples[:limit]

    print(f"Listing published datasets: {PROGRESS_LISTING_QUERY}")
    index = list_published_datasets()

    rows = []
    for entry in samples:
        miniaod = entry["miniaod"]
        matches = index.get(
            (extract_dataset_name(miniaod), crab_vername(miniaod)), []
        )
        rows.append((entry, matches, select_candidates(entry, matches)))

    # The MiniAOD counts are the reference: the sheet's Events column can
    # be stale
    to_query = sorted(
        {d for _, _, cands in rows for d in cands}
        | {e["miniaod"] for e, _, _ in rows}
    )
    print(f"Querying event counts of {len(to_query)} datasets "
          f"for {len(samples)} spreadsheet rows")
    events = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(query_dataset_events, d): d for d in to_query
        }
        for done, future in enumerate(as_completed(futures), start=1):
            events[futures[future]] = future.result()
            print_progress_bar(done, len(to_query))
    if to_query:
        sys.stdout.write("\n")
        sys.stdout.flush()

    progress_root = Path("sample_progress") / str(year)
    progress_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    progress_path = progress_root / f"{timestamp}__{year}.txt"

    status_counts = Counter()
    total_expected_events = 0
    total_published_events = 0
    disagreements = []
    das_errors = []
    multiple = []

    with open(progress_path, "w", encoding="utf-8") as progress_out:
        for entry, matches, candidates in rows:
            sheet_events = entry.get("events")
            miniaod_events = events[entry["miniaod"]]
            expected = miniaod_events or sheet_events
            if candidates:
                # DAS errors (None) sort last, so a good count wins
                chosen = max(
                    candidates,
                    key=lambda d: -1 if events[d] is None else events[d],
                )
                found = events[chosen]
                status = progress_status(expected, found)
            else:
                chosen, found, status = "", None, "NOT_FOUND"

            status_counts[status] += 1
            total_expected_events += expected or 0
            total_published_events += found or 0

            sheet_status = entry.get("status", "")
            if (sheet_status.lower() == "done"
                    and status not in ("COMPLETE", "FOUND")) or (
                    sheet_status.lower() == "not started" and candidates):
                disagreements.append(
                    f"  row {entry['row']}: sheet '{sheet_status}' vs DAS "
                    f"{status} ({found or 0}/{expected or '?'}) "
                    f"{extract_dataset_name(entry['miniaod'])}/"
                    f"{extract_campaign_name(entry['miniaod'])}"
                )

            if miniaod_events is None:
                das_errors.append(f"  row {entry['row']}: {entry['miniaod']}")
            if status == "DAS_ERROR":
                das_errors.append(f"  row {entry['row']}: {chosen}")
            if len(matches) > 1:
                multiple.append(f"  row {entry['row']}: {chosen}")

            progress_out.write(
                format_progress_line(
                    entry.get("assignment", "N/A"),
                    extract_dataset_name(entry["miniaod"]),
                    entry["miniaod"],
                    chosen or default_progress_dataset_name(entry["miniaod"]),
                    miniaod_events or 0,
                    found or 0,
                )
                + "\n"
            )

    print("\n=== Progress Summary ===")
    for status, count in sorted(status_counts.items()):
        print(f"  {status:<10} {count}")
    print(f"  Expected events:  {total_expected_events:,}")
    print(f"  Published events: {total_published_events:,}")
    if disagreements:
        print("\nSpreadsheet status disagrees with DAS "
              f"({len(disagreements)}):")
        print("\n".join(disagreements))
    if multiple:
        print("\nSeveral published datasets matched, picked "
              f"({len(multiple)}):")
        print("\n".join(multiple))
    if das_errors:
        print(f"\nDAS query failed, written as 0 events ({len(das_errors)}):")
        print("\n".join(das_errors))

    print(f"\nWrote progress report to {progress_path}")


def print_report(total_checked, issues):
    print("\n=== Validation Summary ===")
    print(f"Checked NanoAOD datasets: {total_checked}")
    print(f"Issues found: {len(issues)}")

    if not issues:
        print("No missing or mismatched entries found.")
        return

    for idx, issue in enumerate(issues, start=1):
        print(f"\n[{idx}] {issue['type']}")
        print(f"  NanoAOD: {issue.get('nanoaod', '')}")
        if issue.get("expected_miniaod"):
            print(f"  MiniAOD in spreadsheet: {issue['expected_miniaod']}")
        if issue.get("found_parents"):
            print("  Parents found in DAS:")
            for parent in issue["found_parents"]:
                print(f"    - {parent}")
        if issue.get("suggested_miniaod"):
            print(
                "  Suggested MiniAOD to add/use: "
                f"{issue['suggested_miniaod']}"
            )
        if issue.get("details"):
            print(f"  Details: {issue['details']}")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate year-based data/mc confs from spreadsheet.csv and "
            "validate "
            "NanoAOD/MiniAOD via DAS"
        )
    )
    parser.add_argument(
        "year",
        help=(
            "Year used to pick the spreadsheet and output filenames "
            "(e.g. 2024)"
        ),
    )
    parser.add_argument(
        "--user",
        default=None,
        help=(
            "If provided, only entries assigned to this user are written "
            "to the output config"
        ),
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip DAS validation checks",
    )

    parser.add_argument(
        "--track-progress",
        action="store_true",
        help="Check publication progress of the new NanoAOD samples",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="With --track-progress: only check the first N spreadsheet rows",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="With --track-progress: number of parallel DAS queries",
    )

    parser.add_argument(
        "--skip-write",
        action="store_true",
        help="Skip writing output config files (only perform checks)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    csv_path = Path("spreadsheet.csv")
    try:
        download_spreadsheet(args.year, csv_path)
    except (ValueError, RuntimeError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    entries = parse_spreadsheet(csv_path)

    if args.track_progress:
        if os.system("which dasgoclient > /dev/null 2>&1") != 0:
            print(
                "ERROR: dasgoclient is not available in PATH. "
                "Install/setup DAS client first."
            )
            sys.exit(2)

        try:
            run_progress_check(
                entries,
                args.year,
                requested_user=args.user,
                limit=args.limit,
                workers=args.workers,
            )
        except RuntimeError as err:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(1)
        return

    if not args.skip_write:
        mc_path, data_path, mc_selected, data_selected = write_split_confs(
            entries,
            year=args.year,
            requested_user=args.user,
        )
        print(f"Wrote {len(mc_selected)} MC datasets to {mc_path}")
        print(f"Wrote {len(data_selected)} Data datasets to {data_path}")
        if args.user:
            print(
                "Filter used for output config: Assignment contains "
                f"'{args.user}'"
            )

    if args.skip_check:
        return

    if os.system("which dasgoclient > /dev/null 2>&1") != 0:
        print(
            "ERROR: dasgoclient is not available in PATH. "
            "Install/setup DAS client first."
        )
        sys.exit(2)

    total_checked, issues = validate_datasets(
        entries, requested_user=args.user
    )
    print_report(total_checked, issues)


if __name__ == "__main__":
    main()
