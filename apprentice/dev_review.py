"""Dev-set review (D24): export the dev texts for a full manual review, then write the
reviewed labels back into the manifest's `dev_reviewed_label` field (before the freeze).

  python3 -m apprentice.dev_review export     # -> splits/dev_review_v1.csv (open in Excel/Numbers)
  python3 -m apprentice.dev_review apply      # reads the CSV back into splits/split_v1.jsonl

In the CSV, `reviewed_label` is pre-filled with the current (lightly reviewed) label:
change it only where you disagree, using IN_SCOPE / NEEDS_VERIFICATION / OUT, and put
a short reason in `note`. Labelling conventions: vendor/golden/golden_set_ecgt_100_README.md.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter

from apprentice.check_split import DEFAULT_MANIFEST, load_manifest
from apprentice.data import LABELS, ROOT

CSV_PATH = ROOT / "splits" / "dev_review_v1.csv"
FIELDS = ["text_id", "text", "light_label", "light_triggers", "reviewed_label", "note"]


def export():
    rows = [r for r in load_manifest() if r["suite"] == "dev"]
    rows.sort(key=lambda r: (r["gold_label"], r["norm"]))
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:   # BOM so Excel reads UTF-8
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({"text_id": r["text_id"], "text": r["text"], "light_label": r["gold_label"],
                        "light_triggers": " ".join(r["gold_triggers"]),
                        "reviewed_label": r["dev_reviewed_label"] or r["gold_label"], "note": ""})
    print(f"wrote {CSV_PATH} ({len(rows)} rows)")


def apply():
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reviewed = {r["text_id"]: r for r in csv.DictReader(f)}
    bad = {k: r["reviewed_label"] for k, r in reviewed.items() if r["reviewed_label"].strip() not in LABELS}
    if bad:
        sys.exit(f"invalid reviewed_label values: {bad}")
    manifest = load_manifest()
    changed = Counter()
    for r in manifest:
        if r["suite"] == "dev":
            if r["text_id"] not in reviewed:
                sys.exit(f"dev text {r['text_id']} missing from the CSV")
            new = reviewed[r["text_id"]]["reviewed_label"].strip()
            r["dev_reviewed_label"] = new
            r["dev_review_note"] = reviewed[r["text_id"]]["note"].strip() or None
            if new != r["gold_label"]:
                changed[(r["gold_label"], new)] += 1
    with open(DEFAULT_MANIFEST, "w", encoding="utf-8") as f:
        for r in manifest:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"applied {len(reviewed)} reviewed labels; changed {sum(changed.values())}: {dict(changed)}")


if __name__ == "__main__":
    {"export": export, "apply": apply}[sys.argv[1] if len(sys.argv) > 1 else "export"]()
