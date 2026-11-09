"""Render a saved study sheet (Markdown) as a 1500 x 1000 gallery page.

Usage: python -I gallery/src/render_sheet.py SHEET.md OUT.html "caption text"
Only the subset of Markdown used by study sheets is handled. Standard library only.
"""
import html
import re
import sys


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t


def blocks(md):
    out, table, lst = [], [], None
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                table.append(cells)
            continue
        if table:
            rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in table if any(r))
            out.append(f"<table>{rows}</table>")
            table = []
        m = re.match(r"^(\d+)\.\s+(.*)$", line)
        if line.startswith("- ") or m:
            kind = "ul" if line.startswith("- ") else "ol"
            if lst != kind:
                if lst:
                    out.append(f"</{lst}>")
                out.append(f"<{kind}>")
                lst = kind
            out.append(f"<li>{inline(line[2:] if kind == 'ul' else m.group(2))}</li>")
            continue
        if lst:
            out.append(f"</{lst}>")
            lst = None
        if not line.strip() or line.strip() == "---":
            continue
        h = re.match(r"^(#{1,3})\s+(.*)$", line)
        if h:
            n = len(h.group(1))
            out.append(f"<h{n}>{inline(h.group(2))}</h{n}>")
        else:
            out.append(f"<p>{inline(line)}</p>")
    if lst:
        out.append(f"</{lst}>")
    return "\n".join(out)


def main():
    src, dst, caption = sys.argv[1], sys.argv[2], sys.argv[3]
    md = open(src, encoding="utf-8").read()
    head, _, rest = md.partition("## Phrases")
    phrases, _, quiz = rest.partition("## Self")
    quiz = "## Self" + quiz.split("## Answers")[0]
    first = "\n### ".join(phrases.split("\n### ")[:4])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Study sheet</title><style>
:root {{ --bg:#f6f4ef; --ink:#1c1c1e; --muted:#5d5d63; --line:#d9d5cc; --accent:#0f6e66; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
html,body {{ width:1500px; height:1000px; background:var(--bg); color:var(--ink); font-family:"Segoe UI",Arial,sans-serif; }}
.wrap {{ display:grid; grid-template-columns: 1fr 1fr; gap:28px; padding:44px 56px 0; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:26px 30px; height:880px; overflow:hidden; position:relative; }}
.card:after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:70px; background:linear-gradient(rgba(255,255,255,0),#fff); }}
h1 {{ font-size:25px; margin-bottom:8px; }} h2 {{ font-size:20px; margin:14px 0 8px; color:var(--accent); }}
h3 {{ font-size:18px; margin:14px 0 4px; }}
p {{ font-size:14px; color:var(--muted); margin-bottom:8px; }}
table {{ border-collapse:collapse; font-size:14px; margin:6px 0 4px; width:100%; }}
td {{ border-bottom:1px solid #eee; padding:4px 8px 4px 0; vertical-align:top; }} td:first-child {{ color:var(--muted); width:42%; }}
ul {{ list-style:none; font-size:15px; line-height:1.5; }} ol {{ font-size:15.5px; line-height:1.55; padding-left:24px; }}
ol li {{ margin-bottom:6px; }}
i {{ color:var(--accent); }}
.cap {{ position:absolute; left:56px; bottom:22px; font-size:15px; color:var(--muted); }}
</style></head><body><div class="wrap">
<div class="card">{blocks(head)}<h2>Phrases</h2>{blocks(first)}</div>
<div class="card">{blocks(quiz)}</div>
</div><div class="cap">{html.escape(caption)}</div></body></html>"""
    open(dst, "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    main()
