#!/usr/bin/env python3
import json
import sys
from datetime import datetime
import os

QUARANTINE_PATH = os.path.join(os.path.dirname(__file__), "flaky_tests.json")


# Load quarantine
def load_quarantine(path=QUARANTINE_PATH):
    if not os.path.exists(path):
        return {"tests": [], "last_updated": "1970-01-01"}

    with open(path, "r") as f:
        return json.load(f)


# Save quarantine
def save_quarantine(data, path=QUARANTINE_PATH):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# Generate filter
def generate_filter(out_path="filter.txt"):
    quarantine = load_quarantine()

    if len(quarantine["tests"]) == 0:
        filter_expr = ""
    else:
        parts = [f"not {t.split('::')[-1]}" for t in quarantine["tests"]]
        filter_expr = " and ".join(parts)

    with open(out_path, "w") as f:
        f.write(filter_expr)

    print(f"filter.txt successfully generated: {filter_expr}")


# Update quarentine
def update_quarantine(report_path="flaky_report.json"):
    if not os.path.exists(report_path):
        print("[ERROR] File flaky_report.json not found.")
        sys.exit(1)

    with open(report_path, "r") as f:
        report = json.load(f)

    quar = load_quarantine()

    for test_name, data in report["tests"].items():
        if data.get("is_flaky", False):
            if test_name not in quar["tests"]:
                quar["tests"].append(test_name)

    quar["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    save_quarantine(quar)
    print("Quarantine updated:", quar)


# Interface
def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python quarantine.py generate-filter")
        print("  python quarantine.py update")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "generate-filter":
        generate_filter()
    elif cmd == "update":
        update_quarantine()
    else:
        print(f"[ERROR] Command not found: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
