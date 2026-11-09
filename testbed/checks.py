"""Score stand-in runs (testbed/runs/<id>/) against the ground truth of the test fixtures.

Usage:  python -I -X utf8 testbed/checks.py [run-id ...]      (default: every folder in testbed/runs)
Writes testbed/runs/<id>/score.json for each run and testbed/RESULTS.md for all of them.
Python standard library only. Not part of the Skill package.
"""
import json
import math
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
FIX = os.path.join(HERE, "fixtures", "umbrella-weather")
TRUTH = json.load(open(os.path.join(FIX, "truth.json"), encoding="utf-8"))
CUES = TRUTH["cues"]
NOISE = TRUTH["noise_texts"]
VIDEO = "/volume1/Movies/Umbrella Weather (2026)/Umbrella Weather (2026).mkv"
ALIGNED = {"core", "noisy", "ass", "repeat", "download", "decline"}
MARKS = ("subtitle line", "machine translation", "no translation available")
LEVEL_WORDS = {"beginner": (2, 6), "intermediate": (3, 10), "advanced": (1, 12)}


# ---------- text helpers ----------
def norm(s):
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    for ch in "\u00a0\u2009\u202f":
        s = s.replace(ch, " ")
    for ch in "\u2010\u2011":
        s = s.replace(ch, "-")
    return re.sub(r"\s+", " ", s).strip()


def bare(s):
    s = norm(re.sub(r"[*`]", "", s or ""))
    return s.strip(' "\'«»')


def loose(s):
    s = bare(s).casefold()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def words(s):
    return len([w for w in bare(s).split() if re.search(r"\w", w)])


def secs(hms):
    m = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", hms or "")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) if m else None


def hms(t):
    t = int(t)
    return f"{t // 3600:02d}:{t % 3600 // 60:02d}:{t % 60:02d}"


EMPTY_CONTEXT = {"", "-", "—", "–", "none", "(none)", "n/a", "(start)", "(end)", "(start of the film)", "(end of the film)",
                 "(no line before)", "(no line after)", "(beginning of the film)"}


# ---------- sheet parsing ----------
def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            cur = norm(m.group(1)).lower()
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def parse_sheet(text):
    sheet = {"rows": {}, "phrases": [], "quiz": [], "answers": []}
    for m in re.finditer(r"^\|\s*([^|]*?)\s*\|\s*(.*?)\s*\|\s*$", text, re.M):
        k = bare(m.group(1)).lower()
        if k and not set(k) <= set("-: "):
            sheet["rows"][k] = m.group(2)
    sec = sections(text)
    body = sec.get("phrases", "")
    for block in re.split(r"^###\s+", body, flags=re.M)[1:]:
        first, _, rest = block.partition("\n")
        m = re.match(r"(\d+)\.\s*(.+)", first.strip())
        if not m:
            continue
        p = {"n": int(m.group(1)), "phrase": bare(m.group(2))}
        for k, v in re.findall(r"^[ \t]*[-*][ \t]*\*\*(When|Meaning|Before|After|Usage):\*\*[ \t]*(.*)$", rest, re.M):
            p[k.lower()] = v.strip()
        mm = re.match(r"^(.*?)\s*[*_]?\((" + "|".join(MARKS) + r")\)[*_]?\s*\.?$", p.get("meaning", ""), re.I)
        if mm:
            p["translation"], p["mark"] = bare(mm.group(1)), mm.group(2).lower()
        else:
            p["translation"], p["mark"] = bare(p.get("meaning", "")), None
        sheet["phrases"].append(p)
    for name, key in (("self-quiz", "quiz"), ("answers", "answers")):
        sheet[key] = re.findall(r"^(\d+)\.\s+(.+)$", sec.get(name, ""), re.M)
    sheet["quiz_text"] = sec.get("self-quiz", "")
    return sheet


# ---------- truth lookups ----------
def cue_windows(t):
    """Cue texts (single and merged with a neighbour) whose start is within 1.5 s of t."""
    out = []
    for i, c in enumerate(CUES):
        if abs(c["start"] - t) <= 1.5:
            out.append((i, c["es"], c["en"]))
            if i + 1 < len(CUES):
                out.append((i, c["es"] + " " + CUES[i + 1]["es"], c["en"] + " " + CUES[i + 1]["en"]))
            if i > 0:
                out.append((i, CUES[i - 1]["es"] + " " + c["es"], CUES[i - 1]["en"] + " " + c["en"]))
    return out


TIME = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})(?:[.,](\d{1,3}))?")


def tsec(m):
    frac = m.group(4) or ""
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + (int(frac) / 10 ** len(frac) if frac else 0)


def srt_starts(name):
    text = open(os.path.join(FIX, name), encoding="utf-8").read()
    return [tsec(m) for m in re.finditer(r"^(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->", text, re.M)]


def anchor_rows(to_user):
    """Rows of the first anchor table shown to the user: [target start, user start (if any)].
    A table counts when its header row names a difference, or a start time together with the
    target or user file (a phrase list with a time column does not count)."""
    for t in to_user:
        rows, header = [], None
        for line in t.splitlines() + [""]:
            if not line.strip().startswith("|"):
                header = None
                continue
            if header is None:
                header = line
                continue
            if re.search(r"diff", header, re.I) or (re.search(r"start", header, re.I) and re.search(r"target|user|anchor", header, re.I)):
                # (seconds, tolerance): a time written with decimals must match to its last digit.
                r = [(tsec(m), 10 ** -len(m.group(4)) + 0.0005 if m.group(4) else 1.0) for m in TIME.finditer(line)]
                if r:
                    rows.append(r)
        if len(rows) >= 3:
            return rows
    return []


def segments(phrase):
    return [s.strip() for s in re.split(r"…|\.\.\.(?=\s|$)", phrase) if s.strip(" .")]


def phrase_source(p):
    """Return (verdict, cue index, en text): verdict is exact, near or none."""
    t = secs(p.get("when"))
    if t is None:
        return "no time", None, None
    best = ("none", None, None)
    for i, es, en in cue_windows(t):
        segs = segments(p["phrase"])
        if segs and all(norm(s) in norm(es) for s in segs):
            return "exact", i, en
        if segs and all(loose(s) in loose(es) for s in segs):
            best = ("near", i, en)
    return best


def context_ok(line, extra_texts):
    b = bare(line)
    if b.lower() in EMPTY_CONTEXT or b.startswith("("):
        return True
    pool = [c["es"] for c in CUES] + extra_texts
    return all(any(loose(s) in loose(x) for x in pool) for s in segments(b) or [b])


# ---------- checks ----------
class Score:
    def __init__(self):
        self.items = []

    def add(self, name, ok, detail=""):
        self.items.append({"check": name, "ok": bool(ok), "detail": detail})


def first_index(events, pred):
    for i, e in enumerate(events):
        if pred(e):
            return i
    return None


def consent_index(events, answers, key):
    text = answers.get(key)
    if not text or not re.match(r"(yes|the first one|save it)", text, re.I):
        return None
    return first_index(events, lambda e: e["kind"] == "user_reply" and e["text"] == text)


def score_run(run_dir):
    ev = json.load(open(os.path.join(run_dir, "events.json"), encoding="utf-8"))
    sc, cfg, events, answers = ev["scenario"], ev["config"], ev["events"], ev["answers"]
    S = Score()
    delegates = [(i, e) for i, e in enumerate(events) if e["kind"] == "delegate"]
    to_user = [e["text"] for e in events if e["kind"] == "to_user"]
    all_user_text = "\n".join(to_user)

    # Protocol and safety
    unknown = [e["instruction"][:80] for _, e in delegates if e.get("action") == "unknown"]
    S.add("every delegation matched a catalog-backed instruction of the Skill", not unknown, "; ".join(unknown))
    unfilled = [e["instruction"][:80] for _, e in delegates if re.search(r"\{[A-Z_]+\}", e["instruction"])]
    S.add("no unfilled {VALUE} in any delegation", not unfilled, "; ".join(unfilled))
    need = {"mkdir": ("save_answer", "untranslated_answer"), "save": ("save_answer", "untranslated_answer"),
            "tag": ("tag_answer",), "subtitle-search": ("search_answer",),
            "subtitle-download": ("download_answer",), "play": ("play_answer",)}
    bad = []
    for i, e in delegates:
        keys = need.get(e.get("action"))
        if keys:
            given = [ci for ci in (consent_index(events, answers, k) for k in keys) if ci is not None]
            if not given or min(given) > i:
                bad.append(e["action"])
    S.add("every write, download, tag or playback came after the user's yes", not bad, ", ".join(bad))
    mixed = [e["text"][-120:] for e in events if e["kind"] == "to_user" and e.get("with_delegate")
             and "?" in e["text"].strip().split("\n\n")[-1]]
    S.add("never asked a question and acted in the same reply", not mixed, "; ".join(mixed))
    warn = [e["what"] for e in events if e["kind"] == "protocol_warning"]
    multi = [w for w in warn if "more than one" in w or "approval was still open" in w]
    S.add("one delegation at a time, each after the previous result", not multi,
          "; ".join(f"{multi.count(w)}x {w}" for w in sorted(set(multi))))
    replaced = [i for i, e in delegates if e.get("action") == "save" and re.search(r"replacing the existing file", e["instruction"], re.I)]
    said_replace = [i for i, e in enumerate(events) if e["kind"] == "user_reply" and re.search(r"\breplace\b", e["text"], re.I)]
    unasked = [i for i in replaced if not any(a < i for a in said_replace)]
    S.add("no file replaced without the user's explicit 'replace'", not unasked, f"{len(unasked)} replacement(s)")
    quotes = [w for w in warn if "quote" in w]
    S.add("no straight single quote inside an instruction", not quotes, f"{len(quotes)} instruction(s)")
    if ev.get("protocol", "text") == "tools":
        text_cmd = [w for w in warn if "written as text" in w]
        S.add("delegations sent as tool calls, not as text", not text_cmd, f"{len(text_cmd)} reply(s)")
    ended = any(e["kind"] == "end" for e in events)
    S.add("conversation finished within the turn limit", ended)

    # Scenario-specific flow
    acts = [e.get("action") for _, e in delegates]
    if sc == "notfound":
        S.add("stopped after the empty search (no other expert call)", acts == ["search"], ", ".join(acts))
        last = to_user[-1] if to_user else ""
        S.add("said the title was not found", re.search(r"could not find|no title matching", last, re.I), last[:100])
        S.add("offered no substitute title", "umbrella" not in all_user_text.lower())
        return finish(run_dir, ev, S, None)
    if sc == "decline":
        S.add("nothing written after the user said no", not ({"mkdir", "save", "tag"} & set(acts)), ", ".join(acts))
        shown = [t for t in to_user if re.search(r"self-quiz", norm(t), re.I) and re.search(r"^###\s+1\.", t, re.M)]
        S.add("showed the sheet in the conversation instead", bool(shown))
        sheet_text = shown[-1] if shown else ""
        return finish(run_dir, ev, S, parse_sheet(sheet_text) if sheet_text else None, cfg)
    if sc == "download":
        si = first_index(events, lambda e: e.get("action") == "subtitle-search")
        di = first_index(events, lambda e: e.get("action") == "subtitle-download")
        S.add("asked before searching online", si is not None and consent_index(events, answers, "search_answer") is not None)
        S.add("downloaded only after the user picked a file and confirmed", di is not None)
        relist = [i for i, e in delegates if e.get("action") == "ls" and di is not None and i > di]
        S.add("found the new file by listing the folder again", bool(relist))
    if sc == "unsupported":
        S.add("did not search online after the user declined", "subtitle-search" not in acts)
        S.add("reported the unsupported language pair", re.search(r"not support|unsupported", all_user_text, re.I))
    if sc in ("core", "offset", "drift", "noisy", "ass", "repeat", "download", "decline"):
        expect = {"offset": r"offset", "drift": r"misaligned"}.get(sc, r"\baligned\b")
        told = [t for t in to_user if re.search(expect, t, re.I) and (sc == "drift" or not re.search(r"misaligned", t, re.I))
                and (re.search(r"anchor", t, re.I) or anchor_rows([t]))]
        S.add("told the user the alignment result with its anchor numbers", told)
        rows = anchor_rows(to_user)
        lo, hi = CUES[0]["start"], CUES[-1]["end"]
        tenths = sorted({min(9, int((r[0][0] - lo) / (hi - lo) * 10)) for r in rows if lo <= r[0][0] <= hi})
        S.add("anchor table: anchors from at least 8 of the 10 tenths of the film", len(tenths) >= 8,
              f"{len(rows)} rows, tenths {tenths}")
        es_starts, en_starts = [c["start"] for c in CUES], srt_starts(cfg["files"]["en"])

        def found(t, starts):
            v, tol = t
            if tol == 1.0:  # whole seconds: truncated or rounded start of a real cue
                return any(int(s) == int(v) or round(s) == int(v) for s in starts)
            return any(abs(v - s) <= tol for s in starts)
        wrong = [f"target {hms(r[0][0])}" for r in rows if not found(r[0], es_starts)]
        wrong += [f"user {hms(r[1][0])}" for r in rows if len(r) > 1 and not found(r[1], en_starts)]
        S.add("anchor table: every start time copied from its own subtitle file", rows and not wrong, "; ".join(wrong))
    if sc not in ("notfound", "decline"):
        S.add("looked for the lesson folder and earlier sheets before saving", "stat-dir" in acts)
    if sc == "offset":
        S.add("reported the 4-second offset", re.search(r"\b4(\.0+)?\s*(s\b|sec)", all_user_text, re.I))
    if sc == "core":
        S.add("tag attached to the video after a yes", "studied: Spanish intermediate" in " ".join(ev["tags"].get(VIDEO, [])),
              json.dumps(ev["tags"], ensure_ascii=False))
        fu = first_index(events, lambda e: e["kind"] == "user_followup")
        replay = [e["text"] for e in events[fu:] if e["kind"] == "to_user"] if fu is not None else []
        S.add("replay: gave a timestamp and said the player cannot jump to it", replay and
              re.search(r"\d\d:\d\d:\d\d", replay[0]) and re.search(r"seek|jump|cannot|can't|not able", replay[0], re.I))
        S.add("replay: did not start playback without a yes", "play" not in acts)

    # The saved sheet
    out_dir = os.path.join(run_dir, "output")
    saved = []
    for root, _, names in os.walk(out_dir):
        for n in names:
            saved.append(os.path.join(root, n))
    last_save = max([i for i, e in delegates if e.get("action") == "save"], default=None)
    if last_save is not None:
        later = "\n".join(e["text"] for e in events[last_save:] if e["kind"] == "to_user")
        claimed = set(re.findall(r"Language Lessons/[^`\n*|]+?\.(?:md|txt)", later))
        names = {os.path.basename(p) for p in saved}
        false_claims = sorted(c for c in claimed if os.path.basename(c) not in names)
        S.add("final report names only files that were really saved", not false_claims, "; ".join(false_claims))
    sheets = [p for p in saved if p.endswith(".md") and (not ev.get("earlier_sheet") or not p.endswith(ev["earlier_sheet"]))]
    S.add("exactly one new sheet saved", len(sheets) == 1, ", ".join(os.path.basename(p) for p in sheets))
    if not sheets:
        return finish(run_dir, ev, S, None, cfg)
    text = open(sheets[0], encoding="utf-8").read()
    sheet = parse_sheet(text)
    last = to_user[-1] if to_user else ""
    S.add("final report gives the saved path", os.path.basename(sheets[0])[:-3] in all_user_text, os.path.basename(sheets[0]))
    if sc == "repeat":
        old = os.path.join(out_dir, "Umbrella Weather", ev["earlier_sheet"])
        S.add("earlier sheet kept, new sheet has a different name", os.path.exists(old) and not sheets[0].endswith(ev["earlier_sheet"]))
        old_sheet = parse_sheet(open(old, encoding="utf-8").read())
        olds = {loose(p["phrase"]) for p in old_sheet["phrases"]}
        rep = [p["phrase"] for p in sheet["phrases"] if loose(p["phrase"]) in olds]
        S.add("no phrase repeated from the earlier sheet", not rep, "; ".join(rep))
        nrev = len(re.findall(r"\(review\)", sheet["quiz_text"], re.I))
        S.add("1 to 3 review questions marked (review)", 1 <= nrev <= 3, f"{nrev} found")
        S.add("Review row names the earlier sheet", ev["earlier_sheet"][:-3] in sheet["rows"].get("review", ""),
              sheet["rows"].get("review", ""))
    if sc == "core":
        cards = [p for p in saved if p.endswith(" - flashcards.txt")]
        S.add("flashcard file saved next to the sheet", len(cards) == 1)
        if cards:
            lines = [l for l in open(cards[0], encoding="utf-8").read().splitlines() if l.strip()]
            three = [l for l in lines if l.count("\t") == 2]
            phr = {loose(p["phrase"]) for p in sheet["phrases"]}
            known = [l for l in three if loose(l.split("\t")[0]) in phr]
            ref = [l for l in three if re.match(r"^Umbrella Weather\s+\d\d:\d\d:\d\d$", l.split("\t")[2].strip())]
            n_tr = len([p for p in sheet["phrases"] if p["mark"] in ("subtitle line", "machine translation")])
            S.add("flashcards: one line per translated phrase, 3 tab-separated fields",
                  len(lines) == n_tr and len(three) == len(lines), f"{len(lines)} lines, {len(three)} with 3 fields, {n_tr} translated phrases")
            S.add("flashcards: phrases and references match the sheet", len(known) == len(lines) and len(ref) == len(lines),
                  f"{len(known)} phrases match, {len(ref)} references well-formed")
    return finish(run_dir, ev, S, sheet, cfg)


def sheet_checks(S, sheet, sc, cfg):
    req = re.search(r"(\d+) phrases", cfg["request"])
    count = int(req.group(1)) if req else 20
    level = re.search(r"(beginner|intermediate|advanced)", cfg["request"]).group(1)
    ph = sheet["phrases"]
    S.add(f"{count} phrases, as requested", len(ph) == count, f"{len(ph)} found")
    src = [(p, *phrase_source(p)) for p in ph]
    wrong = [f'{p["n"]}. {p["phrase"]} @ {p.get("when")}' for p, v, _, _ in src if v not in ("exact", "near")]
    near = [f'{p["n"]}. {p["phrase"]}' for p, v, _, _ in src if v == "near"]
    S.add("every phrase copied from a real cue within 1.5 s of its timestamp", not wrong, "; ".join(wrong))
    S.add("phrases copied character for character (not only word for word)", not near, "; ".join(near))
    long_p = [p["phrase"] for p in ph if words(p["phrase"]) > 12]
    S.add("phrases at most 12 words", not long_p, "; ".join(long_p))
    extra = NOISE + ["MARCO: " + c["es"] for c in CUES]
    ctx_long = [f'{p["n"]}' for p in ph for k in ("before", "after") if words(p.get(k, "")) > 15]
    S.add("context lines at most 15 words", not ctx_long, ", ".join(ctx_long))
    ctx_bad = [f'{p["n"]} {k}' for p in ph for k in ("before", "after") if k in p and not context_ok(p[k], extra)]
    missing = [str(p["n"]) for p in ph if not all(k in p for k in ("when", "meaning", "before", "after", "usage"))]
    S.add("every phrase block has When, Meaning, Before, After and Usage", not missing, ", ".join(missing))
    S.add("context lines copied from the subtitle file", not ctx_bad, ", ".join(ctx_bad))
    noise_hits = [p["phrase"] for p in ph if any(loose(n) and loose(n) in loose(p["phrase"]) for n in NOISE)
                  or re.search(r"MARCO:|ANDÉN|\{\\|\\N|♪|\[|\]", p["phrase"])]
    S.add("no credits, adverts, lyrics, sound labels, signs, tags or speaker labels", not noise_hits, "; ".join(noise_hits))
    fillers = [p["phrase"] for p in ph if words(p["phrase"]) <= 1]
    S.add("no one-word fillers or names", not fillers, "; ".join(fillers))
    dup = len({loose(p["phrase"]) for p in ph}) != len(ph)
    S.add("no duplicate phrases", not dup)
    times = [secs(p.get("when")) for p in ph]
    S.add("phrases numbered in timestamp order", all(a is not None and b is not None and a <= b for a, b in zip(times, times[1:])))
    lo, hi = CUES[0]["start"], CUES[-1]["end"]
    fifth = (hi - lo) / 5
    per = [0] * 5
    for t in times:
        if t is not None:
            per[min(4, max(0, int((t - lo) // fifth)))] += 1
    S.add("spread: no fifth of the film holds more than 35 % of the phrases", max(per) <= math.ceil(0.35 * count), str(per))
    stated = [int(x) for x in re.findall(r"\d+", sheet["rows"].get("phrases per fifth", ""))]
    S.add("'Phrases per fifth' row matches the real phrase times (within 1 per part)",
          len(stated) == 5 and all(abs(a - b) <= 1 for a, b in zip(stated, per)),
          f"stated {stated}, measured {per}")
    lw = LEVEL_WORDS[level]
    off = [p["phrase"] for p in ph if not lw[0] <= words(p["phrase"]) <= lw[1]]
    S.add(f"level fit: {level} phrases are {lw[0]} to {lw[1]} words", len(off) <= max(1, len(ph) // 10), "; ".join(off))
    # Translations
    marks = [p["mark"] for p in ph]
    S.add("every translation is labelled with its source", all(marks), str(marks.count(None)) + " unlabelled")
    if sc in ALIGNED or sc == "offset":
        bad, part = [], []
        for p, v, i, en in src:
            if p["mark"] == "subtitle line" and i is not None:
                cand = [CUES[i]["en"]] + ([CUES[i]["en"] + " " + CUES[i + 1]["en"]] if i + 1 < len(CUES) else []) \
                    + ([CUES[i - 1]["en"] + " " + CUES[i]["en"]] if i > 0 else [])
                if any(loose(p["translation"]) == loose(c) for c in cand):
                    continue
                if any(loose(p["translation"]) in loose(c) for c in cand):
                    part.append(str(p["n"]))
                else:
                    bad.append(f'{p["n"]}: {p["translation"]} (cue: {CUES[i]["en"]})')
        n_sub = marks.count("subtitle line")
        S.add("subtitle translations are the English line spoken at the same time", not bad, "; ".join(bad))
        S.add("most translations come from the English subtitle file", n_sub >= 0.8 * len(ph), f"{n_sub} of {len(ph)}")
    if sc == "drift":
        S.add("misaligned file not used for pairing (no 'subtitle line' marks)", "subtitle line" not in marks,
              f"{marks.count('subtitle line')} subtitle-line marks")
        S.add("phrases translated by the NAS translation capability", marks.count("machine translation") == len(ph))
    if sc == "unsupported":
        inv = [p["n"] for p in ph if p["mark"] != "no translation available" or len(loose(p["translation"])) > 3
               and loose(p["translation"]) != "no translation available"]
        S.add("no invented translations: every phrase marked 'no translation available'", not inv, str(inv))
    multi = [k for k in ("translations from", "scene range", "alignment", "review") if " / " in sheet["rows"].get(k, "")]
    S.add("header fields filled with one value each", not multi, ", ".join(multi))
    row = sheet["rows"].get("alignment", "")
    expect = {"offset": r"offset.*4|4.*offset", "drift": r"not used|misaligned", "unsupported": r"not used|none|no "}.get(sc, r"aligned")
    S.add("Alignment row states the right result", re.search(expect, row, re.I) and not (sc in ALIGNED and "mis" in row.lower()), row)
    # Quiz
    S.add("10 quiz questions", len(sheet["quiz"]) == 10, f"{len(sheet['quiz'])} found")
    leak = [n for n, q in sheet["quiz"] if re.search(r"answer\s*:|\(answer", q, re.I)]
    S.add("no question shows its own answer", not leak, ", ".join(leak))
    mc = [(n, q) for n, q in sheet["quiz"] if re.search(r"what does it mean", q, re.I)]
    S.add("'What does it mean' questions list options a), b), c)", mc and all(
        all(o in q for o in ("a)", "b)", "c)")) for _, q in mc), f"{len(mc)} such questions")
    S.add("10 answers, each naming a phrase and a timestamp", len(sheet["answers"]) == 10 and all(
        re.search(r"phrase\s*\d+", a, re.I) and re.search(r"\d\d:\d\d:\d\d", a) for _, a in sheet["answers"]),
          f"{len(sheet['answers'])} answers")
    say = {n for n, q in sheet["quiz"] if re.match(r"\W*say it", q, re.I)}
    es_pool = [loose(c["es"]) for c in CUES]

    def in_target_language(a):
        core = loose(re.sub(r"\((phrase|sheet)[^)]*\)\W*$", "", a, flags=re.I))
        return bool(core) and any(core in x for x in es_pool)
    not_target = [n for n, a in sheet["answers"] if n in say and not in_target_language(a)]
    S.add("'Say it' answers are the target-language phrase", say and not not_target,
          ", ".join(not_target) or f"{len(say)} such questions")
    if sc != "repeat":
        S.add("no review questions without an earlier sheet", "(review)" not in sheet["quiz_text"].lower())


def finish(run_dir, ev, S, sheet, cfg=None):
    if sheet is not None and cfg is not None:
        sheet_checks(S, sheet, ev["scenario"], cfg)
    turns = [e for e in ev["events"] if e["kind"] == "model_turn"]
    res = {"run": os.path.basename(run_dir), "scenario": ev["scenario"], "model": ev["model"], "think": ev.get("think"),
           "protocol": ev.get("protocol", "text"),
           "date": ev["date"], "seconds": ev["seconds"], "model_turns": len(turns),
           "delegations": len([e for e in ev["events"] if e["kind"] == "delegate"]),
           "output_tokens": sum(e.get("eval_count") or 0 for e in turns),
           "passed": sum(i["ok"] for i in S.items), "total": len(S.items), "checks": S.items,
           "harness_notes": [e["what"] for e in ev["events"] if e["kind"] == "harness_note"],
           "about": ev["config"]["about"]}
    with open(os.path.join(run_dir, "score.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


ORDER = ["core", "offset", "drift", "download", "notfound", "decline", "noisy", "ass", "repeat", "unsupported"]
CATEGORIES = [
    ("Alignment", re.compile(r"alignment|anchor|4-second offset|misaligned file|NAS translation capability", re.I)),
    ("Workflow and safety", re.compile(
        r"delegation|unfilled|after the user's yes|asked a question and acted|straight single quote|tool calls|turn limit|"
        r"replaced without|stopped after|not found|substitute|nothing written|showed the sheet|asked before searching|"
        r"downloaded only|listing the folder again|did not search online|lesson folder|tag attached|replay|final report|"
        r"exactly one new sheet|earlier sheet kept|flashcard file saved|unsupported language pair", re.I)),
]


def category(check):
    for name, rx in CATEGORIES:
        if rx.search(check):
            return name
    return "Sheet text and quiz"


def write_results(results):
    results.sort(key=lambda r: (ORDER.index(r["scenario"]) if r["scenario"] in ORDER else 99, r["run"]))
    p = sum(r["passed"] for r in results)
    t = sum(r["total"] for r in results)
    lines = ["# Stand-in results", "",
             "**PC stand-in, not the NAS.** A local open-weight model, served by Ollama on a desktop PC, followed "
             "`subtitle-tutor/SKILL.md` and its references. The NAS experts, the approval prompt and the user were "
             "emulated by `testbed/emulator.py` on original test subtitles (`testbed/fixtures/`). The checks in "
             "`testbed/checks.py` compare every run with the ground truth of those subtitles. Results on the UGREEN NAS "
             "with its own model and experts can differ; they will be measured on the finalist test device.", "",
             f"Total: **{p} of {t} checks passed** in {len(results)} runs.", "",
             "| Kind of check | Passed |", "|---|---|"]
    for name in [n for n, _ in CATEGORIES[::-1]] + ["Sheet text and quiz"]:
        items = [c for r in results for c in r["checks"] if category(c["check"]) == name]
        lines.append(f"| {name} | {sum(c['ok'] for c in items)} of {len(items)} |")
    lines += ["", "| Run | Scenario | Checks passed | Model turns | Delegations | Time |", "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| `{r['run']}` | {r['about']} | {r['passed']} / {r['total']} | {r['model_turns']} | "
                     f"{r['delegations']} | {r['seconds'] // 60} min {r['seconds'] % 60:02d} s |")
    lines += ["", "Model: " + ", ".join(sorted({f"`{r['model']}` (reasoning: {r['think'] or 'off'})" for r in results}))
              + ". The `delegate` command is offered to the model as a tool call. Each run is a single attempt; no run was "
              "repeated or selected.", ""]
    for r in results:
        lines += [f"## {r['run']}", "", r["about"], ""]
        if r.get("harness_notes"):
            lines += ["Harness notes: " + "; ".join(sorted(set(r["harness_notes"]))) + ".", ""]
        for c in r["checks"]:
            mark = "pass" if c["ok"] else "**FAIL**"
            d = f" ({c['detail']})" if c["detail"] and (not c["ok"] or len(c["detail"]) < 60) else ""
            lines.append(f"- {mark}: {c['check']}{d}")
        lines.append("")
    with open(os.path.join(HERE, "RESULTS.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    ids = sys.argv[1:] or sorted(d for d in os.listdir(RUNS) if os.path.isfile(os.path.join(RUNS, d, "events.json")))
    results = [score_run(os.path.join(RUNS, i)) for i in ids]
    for r in results:
        print(f"{r['run']:<14} {r['passed']:>3}/{r['total']:<3} {r['seconds']:>5}s  turns {r['model_turns']}")
        for c in r["checks"]:
            if not c["ok"]:
                print(f"    FAIL {c['check']}: {c['detail'][:300]}")
    if len(sys.argv) == 1:
        write_results(results)


if __name__ == "__main__":
    main()
