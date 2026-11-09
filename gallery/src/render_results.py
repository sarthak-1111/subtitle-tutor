"""Render the stand-in results (testbed/runs/*/score.json) as a 1500 x 1000 gallery page.

Usage: python -I gallery/src/render_results.py OUT.html
Standard library only.
"""
import glob
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTBED = os.path.join(HERE, "..", "..", "testbed")
RUNS = os.path.join(TESTBED, "runs")
sys.path.insert(0, TESTBED)
from checks import category  # noqa: E402  (same grouping as testbed/RESULTS.md)
ORDER = ["core", "offset", "drift", "download", "notfound", "decline", "noisy", "ass", "repeat", "unsupported"]
LABEL = {
    "core": "Normal lesson: save with flashcards, tag, replay",
    "offset": "English subtitles 4.0 s late",
    "drift": "English subtitles drifting (other frame rate)",
    "download": "Spanish file missing: confirmed download",
    "notfound": "Title not in the library",
    "decline": "User says no to saving",
    "noisy": "Credits, adverts, lyrics, labels in the file",
    "ass": "Advanced SubStation file, advanced level",
    "repeat": "Second lesson: no repeats, review questions",
    "unsupported": "No English file, unsupported language pair",
}


def main():
    scores = []
    for p in glob.glob(os.path.join(RUNS, "*", "score.json")):
        scores.append(json.load(open(p, encoding="utf-8")))
    scores.sort(key=lambda r: ORDER.index(r["scenario"]) if r["scenario"] in ORDER else 99)
    passed = sum(r["passed"] for r in scores)
    total = sum(r["total"] for r in scores)
    model = ", ".join(sorted({f"{r['model']} ({r['think']} reasoning)" for r in scores}))
    tiles = []
    for name in ("Workflow and safety", "Sheet text and quiz", "Alignment"):
        items = [c for r in scores for c in r["checks"] if category(c["check"]) == name]
        ok = sum(c["ok"] for c in items)
        tiles.append(f"<div class='tile'><div class='k'>{html.escape(name)}</div><div class='v'>{ok} / {len(items)}</div>"
                     f"<div class='bar'><div style='width:{100 * ok / max(1, len(items)):.0f}%'></div></div></div>")
    rows = []
    for r in scores:
        pct = 100 * r["passed"] / r["total"] if r["total"] else 0
        rows.append(f"<tr><td class='s'>{html.escape(r['scenario'])}</td><td>{html.escape(LABEL.get(r['scenario'], r['about']))}</td>"
                    f"<td class='n'>{r['passed']} / {r['total']}</td>"
                    f"<td class='bar'><div style='width:{pct:.0f}%'></div></td></tr>")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Stand-in results</title><style>
:root {{ --bg:#f6f4ef; --ink:#1c1c1e; --muted:#5d5d63; --line:#d9d5cc; --accent:#0f6e66; --warn:#9a5b00; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:1500px; height:1000px; background:var(--bg); color:var(--ink); font-family:"Segoe UI",Arial,sans-serif; }}
.page {{ padding:52px 64px; }}
h1 {{ font-size:40px; }} .sub {{ font-size:20px; color:var(--muted); margin:8px 0 18px; }}
.badge {{ display:inline-block; font-size:15px; font-weight:700; color:var(--warn); background:#fbefdc; padding:5px 12px; border-radius:7px; margin-bottom:22px; }}
.total {{ font-size:22px; margin-bottom:14px; }} .total b {{ color:var(--accent); font-size:30px; }}
table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
.tiles {{ display:flex; gap:18px; margin-bottom:18px; }}
.tile {{ flex:1; background:#fff; border:1px solid var(--line); border-radius:14px; padding:12px 18px; }}
.tile .k {{ font-size:16px; color:var(--muted); }} .tile .v {{ font-size:26px; font-weight:700; margin:2px 0 8px; }}
.tile .bar {{ height:10px; background:#ece8df; border-radius:5px; }} .tile .bar div {{ height:10px; background:var(--accent); border-radius:5px; }}
td {{ padding:8px 18px; border-bottom:1px solid #eee; font-size:18px; }}
td.s {{ font-family:Consolas,monospace; font-size:16px; color:var(--accent); width:150px; }}
td.n {{ width:120px; text-align:right; font-weight:600; }}
td.bar {{ width:260px; }} td.bar div {{ height:12px; background:var(--accent); border-radius:6px; }}
.foot {{ position:absolute; left:64px; bottom:24px; font-size:15px; color:var(--muted); max-width:1370px; }}
</style></head><body><div class="page">
<h1>Off-device stand-in tests</h1>
<div class="sub">Ten scenarios on original test subtitles; every phrase, timestamp, translation and confirmation is checked automatically.</div>
<div class="badge">PC STAND-IN, NOT THE NAS: {html.escape(model)} follows SKILL.md; NAS experts, approvals and user are emulated</div>
<div class="total"><b>{passed} / {total}</b> checks passed, one attempt per scenario</div>
<div class="tiles">{''.join(tiles)}</div>
<table>{''.join(rows)}</table>
</div><div class="foot">Test bench, transcripts and scoring: github.com/sarthak-1111/subtitle-tutor, folder testbed/. Results on the UGREEN NAS will be measured on the finalist testing day.</div></body></html>"""
    open(sys.argv[1], "w", encoding="utf-8").write(page)
    print(f"{passed}/{total} from {len(scores)} runs")


if __name__ == "__main__":
    main()
