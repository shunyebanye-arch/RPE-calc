"""training_log/*.csv から SUMMARY.md を生成する。

    python training_log/summary.py

sets.csv : 1行 = 同一重量・レップ・RPEのセット群 (sets列にセット数)
lift     : SQ / BP / DL / その他は自由記述 (補助種目は e1RM 対象外)
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from rpe_chart import e1rm  # noqa: E402

BIG3 = ("SQ", "BP", "DL")


def load(name):
    with open(ROOT / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    sets = load("sets.csv")
    sessions = {s["date"]: s for s in load("sessions.csv")}

    best = {}                      # lift -> (e1rm, row)
    by_date = defaultdict(list)    # date -> rows
    tonnage = defaultdict(lambda: defaultdict(float))  # date -> lift -> kg
    top_e1rm = defaultdict(dict)   # lift -> date -> best e1rm that day

    for r in sets:
        lift = r["lift"].strip().upper()
        w, reps, n = float(r["weight"]), int(r["reps"]), int(r["sets"] or 1)
        rpe = float(r["rpe"]) if r["rpe"] else None
        r["_e1rm"] = e1rm(lift, w, reps, rpe) if lift in BIG3 and rpe else None
        by_date[r["date"]].append(r)
        tonnage[r["date"]][lift] += w * reps * n
        if r["_e1rm"]:
            if lift not in best or r["_e1rm"] > best[lift][0]:
                best[lift] = (r["_e1rm"], r)
            d = top_e1rm[lift]
            d[r["date"]] = max(d.get(r["date"], 0), r["_e1rm"])

    out = ["# Training Log Summary", "", "## ベスト e1RM", "",
           "| 種目 | e1RM | セット | 日付 |", "|---|---|---|---|"]
    total = 0
    for lift in BIG3:
        if lift in best:
            v, r = best[lift]
            total += v
            out.append(f"| {lift} | {v:.1f} kg | {r['weight']}x{r['reps']} @{r['rpe']} | {r['date']} |")
        else:
            out.append(f"| {lift} | - | - | - |")
    out += ["", f"**e1RM トータル: {total:.1f} kg**" if len(best) == 3 else "", ""]

    out += ["## e1RM 推移 (日ごとのトップ)", "", "| 日付 | SQ | BP | DL |", "|---|---|---|---|"]
    for date in sorted(by_date):
        cells = [f"{top_e1rm[l][date]:.1f}" if date in top_e1rm[l] else "" for l in BIG3]
        out.append(f"| {date} | " + " | ".join(cells) + " |")

    out += ["", "## セッション", ""]
    for date in sorted(by_date, reverse=True):
        s = sessions.get(date, {})
        meta = []
        if s.get("bodyweight"):
            meta.append(f"体重 {s['bodyweight']}kg")
        if s.get("sleep_h"):
            meta.append(f"睡眠 {s['sleep_h']}h")
        out.append(f"### {date}" + (f"  ({', '.join(meta)})" if meta else ""))
        if s.get("note"):
            out.append(f"_{s['note']}_")
        out.append("")
        out.append("| 種目 | 重量 | レップ×セット | RPE | e1RM | メモ |")
        out.append("|---|---|---|---|---|---|")
        for r in by_date[date]:
            e = f"{r['_e1rm']:.1f}" if r["_e1rm"] else ""
            out.append(f"| {r['lift']} | {r['weight']} | {r['reps']}×{r['sets'] or 1} | {r['rpe']} | {e} | {r['note']} |")
        vol = ", ".join(f"{k} {v:,.0f}kg" for k, v in tonnage[date].items())
        out += ["", f"ボリューム: {vol}", ""]

    (ROOT / "SUMMARY.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:12]))


if __name__ == "__main__":
    main()
