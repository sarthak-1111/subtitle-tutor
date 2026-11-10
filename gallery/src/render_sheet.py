"""Render a saved study sheet (Markdown), and optionally its flashcard file, as a 1500 x 1000 gallery page.

Usage: python -I gallery/src/render_sheet.py SHEET.md OUT.html "caption text" [FLASHCARDS.txt]
Only the subset of Markdown used by study sheets is handled. The text is shown exactly as saved.
Styled following unslop by Damir Sokolovsky (@heydamir), https://github.com/heydamir/unslop, CC BY 4.0.
Standard library only.
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


def decorate(body):
    # Phrase headings get the highlighter; timecodes are set in mono. The words are not changed.
    body = re.sub(r"<h3>(\d+)\.\s*(.*?)</h3>", r"<h3><span class='n'>\1</span><span class='mark'>\2</span></h3>", body)
    return re.sub(r"\b(\d\d:\d\d:\d\d)\b", r"<span class='mono'>\1</span>", body)


def cards_block(path, limit=5):
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    items = []
    for line in lines[:limit]:
        f = (line.split("	") + ["", "", ""])[:3]
        items.append(f"<li><div class='row'><span>{html.escape(f[0])}</span><span class='ref'>{html.escape(f[2])}</span></div>"
                     f"<div class='mean'>{html.escape(f[1])}</div></li>")
    name = path.replace("\\", "/").rsplit("/", 1)[-1]
    return (f"<section class='card side'><h2>Flashcards</h2><p class='file mono'>{html.escape(name)}</p>"
            f"<ul class='cards'>{decorate(''.join(items))}</ul>"
            f"<p class='more'>First {min(limit, len(lines))} of {len(lines)} lines, each with three fields separated by tabs</p></section>")


def main():
    src, dst, caption = sys.argv[1], sys.argv[2], sys.argv[3].rstrip(".")
    cards = cards_block(sys.argv[4]) if len(sys.argv) > 4 else ""
    md = open(src, encoding="utf-8").read()
    head, _, rest = md.partition("## Phrases")
    phrases, _, quiz = rest.partition("## Self")
    quiz = "## Self" + quiz.split("## Answers")[0]
    first = "\n### ".join(phrases.split("\n### ")[:4])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Study sheet</title>
<!-- Styled following unslop by Damir Sokolovsky (@heydamir), https://github.com/heydamir/unslop, CC BY 4.0 -->
<link rel="stylesheet" href="style.css"><style>
.wrap {{ display:grid; grid-template-columns:760px 572px; gap:40px; padding:64px 64px 0; }}
.paper {{ height:856px; overflow:hidden; position:relative; padding:32px 40px; }}
.paper::after {{ content:""; position:absolute; left:0; right:0; bottom:0; height:96px;
  background:linear-gradient(rgba(253,251,247,0), var(--card)); }}
.col {{ display:flex; flex-direction:column; gap:20px; }}
.side {{ padding:24px 28px; }}
h1 {{ font-family:var(--serif); font-weight:500; font-size:30px; line-height:36px; letter-spacing:-0.01em; }}
p {{ font-size:14px; line-height:20px; color:var(--text-2); }}
h1 + p {{ margin-top:8px; }}
table {{ width:100%; border-collapse:collapse; margin-top:16px; font-size:14px; line-height:20px; }}
td {{ padding:6px 12px 6px 0; border-top:1px solid var(--hair); vertical-align:top; }}
td:first-child {{ width:40%; color:var(--text-3); }}
h2 {{ margin-top:28px; padding-top:20px; border-top:1px solid var(--hair-2); font-size:15px; line-height:20px; font-weight:500; color:var(--text-2); }}
.side h2 {{ margin-top:0; padding-top:0; border-top:0; }}
h3 {{ margin-top:20px; font-size:19px; line-height:26px; font-weight:500; }}
h3 .n {{ font-family:var(--mono); font-size:13px; color:var(--text-3); margin-right:8px; }}
ul {{ list-style:none; margin-top:8px; font-size:14px; line-height:22px; }}
b {{ font-weight:500; color:var(--text-3); }}
i {{ font-style:normal; color:var(--text-3); }}
ol {{ margin-top:12px; padding-left:28px; font-size:14px; line-height:22px; }}
ol li {{ margin-bottom:6px; padding-left:4px; }}
ol li::marker {{ font-family:var(--mono); font-size:12px; color:var(--text-3); }}
.file {{ margin-top:4px; font-size:12px; line-height:16px; color:var(--text-3); }}
ul.cards {{ margin-top:12px; font-size:14px; line-height:20px; }}
ul.cards li {{ padding:7px 0; border-top:1px solid var(--hair); }}
ul.cards .row {{ display:flex; justify-content:space-between; gap:16px; }}
ul.cards .ref {{ color:var(--text-3); white-space:nowrap; font-size:13px; }}
ul.cards .mean {{ color:var(--text-2); }}
.more {{ margin-top:10px; font-size:12px; line-height:16px; color:var(--text-3); }}
</style></head><body><div class="wrap">
<article class="card paper">{decorate(blocks(head))}<h2>Phrases</h2>{decorate(blocks(first))}</article>
<div class="col"><section class="card side">{decorate(blocks(quiz))}</section>{cards}</div>
</div><div class="foot">{html.escape(caption)}</div></body></html>"""
    open(dst, "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    main()
