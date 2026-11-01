"""Dev-set review (D24, D33): export the dev texts to Excel for a full manual review, then write the
reviewed labels back into the manifest's `dev_reviewed_label` field (before the freeze).

  python3 -m apprentice.dev_review export     # -> splits/dev_review_v1.xlsx
  python3 -m apprentice.dev_review apply      # reads the workbook back into splits/split_v1.jsonl

In the workbook, `reviewed_label` (yellow) is pre-filled with the current (lightly reviewed) label:
change it only where you disagree, choosing from the dropdown, and add a short reason in `note`.
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from apprentice.check_split import DEFAULT_MANIFEST, load_manifest
from apprentice.data import LABELS, ROOT

XLSX_PATH = ROOT / "splits" / "dev_review_v1.xlsx"
HEADERS = ["text_id", "claim", "light_label", "light_triggers", "reviewed_label", "note"]
FONT, BOLD = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True)
YELLOW = PatternFill("solid", start_color="FFFF00")
GREY = PatternFill("solid", start_color="D9D9D9")

README = [
    ("How to review the dev set (150 claims, about 1–2 hours)", True),
    ("", False),
    ("1. Go to the 'review' sheet. Each row is one unique claim from the reserve sets (lighter review so far).", False),
    ("2. Edit only the two yellow columns: reviewed_label and note. Leave the grey columns unchanged.", False),
    ("3. reviewed_label is pre-filled with the current label. Change it only where you disagree, using the dropdown:", False),
    ("     IN_SCOPE = problematic as written (vague/undefined green or natural wording, offset-based climate neutrality,", False),
    ("                comparison without comparator, brand eco-slogan, vague sustainable sourcing/farming)", False),
    ("     NEEDS_VERIFICATION = specific and checkable (certification/organic, recycled/recyclable part, vegan,", False),
    ("                concrete farming practice, named endorsement or comparison, defined term, named pollutant-free)", False),
    ("     OUT = not an ECGT environmental claim (health, taste, performance, tests, origin, DOP/IGP, senza conservanti)", False),
    ("4. When you change a label, write a short reason in note, e.g. «la nota definisce 'naturale' → termine definito».", False),
    ("5. Save the file (keep the .xlsx format and the file name). Then: python3 -m apprentice.dev_review apply", False),
    ("", False),
    ("Conventions: vendor/golden/golden_set_ecgt_100_README.md and the PROJECT CONVENTIONS block in prompts/P_teacher.md.", False),
    ("Rows are sorted by light_label, then alphabetically.", False),
]


def export():
    rows = sorted((r for r in load_manifest() if r["suite"] == "dev"), key=lambda r: (r["gold_label"], r["norm"]))
    wb = Workbook()
    ws = wb.active
    ws.title = "review"
    ws.append(HEADERS)
    for r in rows:
        ws.append([r["text_id"], r["text"], r["gold_label"], " ".join(r["gold_triggers"]),
                   r.get("dev_reviewed_label") or r["gold_label"], r.get("dev_review_note") or ""])
    widths = {"A": 18, "B": 90, "C": 20, "D": 30, "E": 22, "F": 50}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    for row in ws.iter_rows():
        for c in row:
            c.font = BOLD if c.row == 1 else FONT
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if c.row > 1:
                c.fill = YELLOW if c.column_letter in "EF" else GREY
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:F{len(rows) + 1}"
    dv = DataValidation(type="list", formula1=f'"{",".join(LABELS)}"', allow_blank=False,
                        showErrorMessage=True, errorTitle="Invalid label",
                        error="Choose IN_SCOPE, NEEDS_VERIFICATION or OUT")
    ws.add_data_validation(dv)
    dv.add(f"E2:E{len(rows) + 1}")
    rd = wb.create_sheet("read me", 0)
    for text, bold in README:
        rd.append([text])
        rd.cell(rd.max_row, 1).font = BOLD if bold else FONT
    rd.column_dimensions["A"].width = 120
    wb.active = 1
    wb.save(XLSX_PATH)
    print(f"wrote {XLSX_PATH} ({len(rows)} rows)")


def apply():
    ws = load_workbook(XLSX_PATH, data_only=True)["review"]
    header = [c.value for c in ws[1]]
    if header != HEADERS:
        sys.exit(f"unexpected header in {XLSX_PATH.name}: {header}")
    reviewed = {}
    for vals in ws.iter_rows(min_row=2, values_only=True):
        if vals[0]:
            reviewed[str(vals[0])] = {"label": str(vals[4] or "").strip(), "note": str(vals[5] or "").strip()}
    bad = {k: v["label"] for k, v in reviewed.items() if v["label"] not in LABELS}
    if bad:
        sys.exit(f"invalid reviewed_label values: {bad}")
    manifest = load_manifest()
    changed = Counter()
    for r in manifest:
        if r["suite"] != "dev":
            continue
        if r["text_id"] not in reviewed:
            sys.exit(f"dev text {r['text_id']} missing from the workbook")
        new = reviewed[r["text_id"]]["label"]
        r["dev_reviewed_label"], r["dev_review_note"] = new, reviewed[r["text_id"]]["note"] or None
        if new != r["gold_label"]:
            changed[f"{r['gold_label']} -> {new}"] += 1
    with open(DEFAULT_MANIFEST, "w", encoding="utf-8") as f:
        for r in manifest:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"applied {len(reviewed)} reviewed labels; changed {sum(changed.values())}: {dict(changed)}")


if __name__ == "__main__":
    {"export": export, "apply": apply}[sys.argv[1] if len(sys.argv) > 1 else "export"]()
