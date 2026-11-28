"""sets.csv から BIG3(SQ/BP/DL)と PauseSQ の e1RM を計算して e1rm.json に書く。

    python training_log/export_e1rm.py

e1RM = 重量 ÷ RPEチャートの係数(rpe_chart.py。BPはBP用、それ以外はSQ/DL用)。
RPEが記録されていない行は除く。週(W1〜)は 2026-11-02(月)始まりで数える。
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from rpe_chart import e1rm  # noqa: E402

START = date(2026, 11, 2)
LIFTS = {"SQ": "SQ", "BP": "BP", "DL": "DL", "PAUSESQ": "PauseSQ"}

rows = []
with open(ROOT / "sets.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        lift = LIFTS.get(r["lift"].strip().upper())
        if not lift or not r["rpe"]:
            continue
        w, reps, rpe = float(r["weight"]), int(r["reps"]), float(r["rpe"])
        v = e1rm("SQ" if lift == "PauseSQ" else lift, w, reps, rpe)
        if v is None:
            continue
        d = date.fromisoformat(r["date"])
        rows.append({"date": r["date"], "week": f"W{(d - START).days // 7 + 1}",
                     "lift": lift, "weight": w, "reps": reps, "rpe": rpe,
                     "e1rm": round(v, 1)})

code = Path(__file__).read_text(encoding="utf-8")
chart = (ROOT.parent / "rpe_chart.py").read_text(encoding="utf-8")
out = {"rows": rows, "meta": [
    {"label": "export_e1rm.py", "value": code, "type": "code", "lang": "python"},
    {"label": "rpe_chart.py", "value": chart, "type": "code", "lang": "python"},
    {"label": "Input", "value": "training_log/sets.csv"},
]}
(ROOT / "e1rm.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(rows), "rows")
