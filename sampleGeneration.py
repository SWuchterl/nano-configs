#!/usr/bin/env python3
import argparse
import csv
import os
import subprocess
import sys
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
}


def normalize(text):
    return (text or "").strip()


def find_header_and_indices(rows):
    needed = {"miniaod", "nanoaod", "assignment", "type"}
    for i, row in enumerate(rows):
        lowered = [normalize(c).lower() for c in row]
        if not needed.issubset(set(lowered)):
            continue
        return i, {
            "miniaod": lowered.index("miniaod"),
            "nanoaod": lowered.index("nanoaod"),
            "assignment": lowered.index("assignment"),
            "type": lowered.index("type"),
        }
    raise ValueError(
        "Could not find CSV header with MiniAOD, NanoAOD, Assignment, "
        "and Type columns"
    )


def parse_spreadsheet(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header_idx, col = find_header_and_indices(rows)
    entries = []

    for row in rows[header_idx + 1:]:
        if not row:
            continue
        max_idx = max(col.values())
        if len(row) <= max_idx:
            continue

        miniaod = normalize(row[col["miniaod"]])
        nanoaod = normalize(row[col["nanoaod"]])
        assignment = normalize(row[col["assignment"]])
        sample_type = normalize(row[col["type"]])

        if not nanoaod and not miniaod:
            continue

        entries.append(
            {
                "miniaod": miniaod,
                "nanoaod": nanoaod,
                "assignment": assignment,
                "type": sample_type,
            }
        )

    return entries


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
    data_selected = []
    seen_mc = set()
    seen_data = set()

    for e in entries:
        if requested_user and not assignment_matches(
            e["assignment"], requested_user
        ):
            continue

        sample_type = normalize(e.get("type")).lower()
        if sample_type == "data":
            dataset = e["nanoaod"] or e["miniaod"]
            if not dataset or not dataset.startswith("/"):
                continue
            if dataset in seen_data:
                continue
            seen_data.add(dataset)
            data_selected.append(dataset)
            continue

        dataset = e["miniaod"] or e["nanoaod"]
        if not dataset or not dataset.startswith("/"):
            continue
        if dataset in seen_mc:
            continue
        seen_mc.add(dataset)
        mc_selected.append(dataset)

    with open(mc_path, "w", encoding="utf-8") as mc_out:
        for dataset in mc_selected:
            mc_out.write(dataset + "\n")

    with open(data_path, "w", encoding="utf-8") as data_out:
        for dataset in data_selected:
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

    for e in entries:
        if requested_user and not assignment_matches(
            e["assignment"], requested_user
        ):
            continue

        nano = e["nanoaod"]
        expected_parent = e["miniaod"]
        sample_type = normalize(e.get("type"))

        if not nano or not nano.startswith("/"):
            continue

        total += 1
        print(f"[CHECK] {nano}")

        rc_ds, ds_out, ds_err = run_dasgoclient_query(f"dataset={nano}")
        exists = (rc_ds == 0 and nano in ds_out)

        if not exists:
            issues.append(
                {
                    "type": "missing_nanoaod",
                    "nanoaod": nano,
                    "expected_miniaod": expected_parent,
                    "details": ds_err or "dataset not found in DAS output",
                }
            )
            print("  -> MISSING NanoAOD")
            continue

        rc_parent, parent_out, parent_err = run_dasgoclient_query(
            f"parent dataset={nano}")
        parents = [p for p in parent_out if p.startswith("/")]

        if not expected_parent:
            if parents:
                details = (
                    "MiniAOD column is empty; DAS parent found:\n"
                    f"{parents[0]}"
                )
                suggested_miniaod = parents[0]
            else:
                details = (
                    "MiniAOD column is empty; no parent was returned by DAS. "
                    "Add the missing MiniAOD to the spreadsheet"
                )
                suggested_miniaod = suggest_from_nano(nano)

            issues.append(
                {
                    "type": "missing_expected_miniaod",
                    "nanoaod": nano,
                    "found_parents": parents,
                    "suggested_miniaod": suggested_miniaod,
                    "details": details,
                }
            )
            print(f"  -> WARNING: MiniAOD column is empty: {details}")
            continue

        if rc_parent != 0 or not parents:
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
            print("  -> MISSING parent MiniAOD")
            continue

        if sample_type.lower() != "data":
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
        help="Year used to pick the spreadsheet and output filenames (e.g. 2024)",
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

    mc_path, data_path, mc_selected, data_selected = write_split_confs(
        entries,
        year=args.year,
        requested_user=args.user,
    )
    print(f"Wrote {len(mc_selected)} MC datasets to {mc_path}")
    print(f"Wrote {len(data_selected)} Data datasets to {data_path}")
    if args.user:
        print(
            f"Filter used for output config: Assignment contains '{args.user}'"
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
