"""Render the stand-in results (testbed/runs/*/score.json) as a 1500 x 1000 gallery page.

Usage: python -I gallery/src/render_results.py OUT.html
Styled following unslop by Damir Sokolovsky (@heydamir), https://github.com/heydamir/unslop, CC BY 4.0.
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
# The accent marks one figure only: the share of workflow and safety checks passed.
ACCENT = "Workflow and safety"
ABOUT = {
    "Workflow and safety": "Consent before every write, real results only, one delegation at a time, no substitute titles",
    "Sheet text and quiz": "Exact phrases and times, spread, translations, quiz format",
    "Alignment": "Anchor table, offset and drift detection",
}


def bar(ok, total, accent=False):
    width = 100 * ok / total if total else 0
    return f"<div class='bar{' on' if accent else ''}'><div style='width:{width:.1f}%'></div></div>"


def main():
    scores = []
    for p in glob.glob(os.path.join(RUNS, "*", "score.json")):
        scores.append(json.load(open(p, encoding="utf-8")))
    scores = [r for r in scores if r["scenario"] in ORDER]
    scores.sort(key=lambda r: ORDER.index(r["scenario"]))
    passed = sum(r["passed"] for r in scores)
    total = sum(r["total"] for r in scores)
    model = ", ".join(sorted({f"{r['model']} ({r['think']} reasoning)" for r in scores}))
    cats = []
    for name in ("Workflow and safety", "Sheet text and quiz", "Alignment"):
        items = [c for r in scores for c in r["checks"] if category(c["check"]) == name]
        ok = sum(c["ok"] for c in items)
        cats.append(f"<li><div class='line'><span>{html.escape(name)}</span><span class='num'>{ok} / {len(items)}</span></div>"
                    f"<div class='about'>{html.escape(ABOUT[name])}</div>{bar(ok, len(items), name == ACCENT)}</li>")
    rows = []
    for r in scores:
        rows.append(f"<li><div><div class='lab'>{html.escape(LABEL[r['scenario']])}</div>"
                    f"<div class='id mono'>{html.escape(r['scenario'])}</div></div>"
                    f"{bar(r['passed'], r['total'])}<div class='n num'>{r['passed']} / {r['total']}</div></li>")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Stand-in results</title>
<!-- Styled following unslop by Damir Sokolovsky (@heydamir), https://github.com/heydamir/unslop, CC BY 4.0 -->
<link rel="stylesheet" href="style.css"><style>
.page {{ display:grid; grid-template-columns:520px 804px; gap:48px; padding:64px 64px 0; height:920px; }}
.left {{ display:flex; flex-direction:column; }}
h1 {{ font-family:var(--serif); font-weight:400; font-size:56px; line-height:60px; letter-spacing:-0.03em; }}
.lede {{ margin-top:16px; font-size:18px; line-height:28px; color:var(--text-2); }}
.note {{ margin-top:24px; padding:12px 16px; border-radius:10px; background:var(--raised);
  font-size:14px; line-height:20px; color:var(--text-2); }}
.note b {{ font-weight:500; color:var(--text); }}
.figure {{ margin-top:auto; }}
.big {{ font-size:72px; line-height:72px; font-weight:500; letter-spacing:-0.02em; font-variant-numeric:tabular-nums; }}
.big span {{ color:var(--text-3); font-weight:400; }}
.cap {{ margin-top:8px; font-size:14px; line-height:20px; color:var(--text-2); }}
.cats {{ list-style:none; margin-top:32px; border-top:1px solid var(--hair-2); }}
.cats li {{ padding:12px 0; border-bottom:1px solid var(--hair-2); }}
.cats .line {{ display:flex; justify-content:space-between; font-size:15px; line-height:22px; }}
.num {{ font-variant-numeric:tabular-nums; }}
.cats .num {{ font-size:15px; color:var(--text-2); }}
.cats .about {{ margin-top:2px; font-size:13px; line-height:20px; color:var(--text-3); text-wrap:balance; }}
.cats .bar {{ margin-top:8px; }}
.bar {{ height:4px; border-radius:2px; background:var(--raised); }}
.bar div {{ height:4px; border-radius:2px; background:#a39887; }}
.bar.on div {{ background:var(--accent); }}
.table {{ padding:24px 32px 8px; }}
.table h2 {{ font-size:15px; line-height:20px; font-weight:500; color:var(--text-2); }}
.table .sub {{ margin-top:2px; font-size:13px; line-height:20px; color:var(--text-3); }}
.rows {{ list-style:none; margin-top:16px; }}
.rows li {{ display:grid; grid-template-columns:1fr 200px 72px; align-items:center; gap:24px;
  padding:17px 0; border-top:1px solid var(--hair); }}
.lab {{ font-size:15px; line-height:22px; }}
.id {{ margin-top:2px; font-size:12px; line-height:16px; color:var(--text-3); }}
.n {{ text-align:right; font-size:15px; line-height:20px; color:var(--text-2); }}
</style></head><body><div class="page">
<section class="left">
  <h1>Off-device<br>stand-in tests</h1>
  <p class="lede">Ten scenarios on original test subtitles; every phrase, timestamp, translation and confirmation is checked automatically</p>
  <p class="note"><b>PC stand-in, not the NAS:</b> {html.escape(model)} follows SKILL.md; the NAS experts, approvals and user are emulated</p>
  <div class="figure">
    <div class="big">{passed}<span> / {total}</span></div>
    <p class="cap">Checks passed in the final round, one attempt per scenario</p>
    <ul class="cats">{''.join(cats)}</ul>
  </div>
</section>
<section class="card table">
  <h2>Scenarios</h2>
  <p class="sub">Checks passed per scenario</p>
  <ul class="rows">{''.join(rows)}</ul>
</section>
</div><div class="foot">Test bench, transcripts and scores: github.com/sarthak-1111/subtitle-tutor (folder testbed) · NAS results will be measured on the finalist testing day</div></body></html>"""
    open(sys.argv[1], "w", encoding="utf-8").write(page)
    print(f"{passed}/{total} from {len(scores)} runs")


if __name__ == "__main__":
    main()
