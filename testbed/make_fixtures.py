"""Build the Umbrella Weather subtitle fixtures from script.tsv.

Everything here is original test material written for this testbed (CC0).
Outputs go to testbed/fixtures/umbrella-weather/:
  es.srt, en.srt          aligned pair (same timings)
  en.shift4.srt           English shifted by +4.000 s (constant offset)
  en.drift.srt            English converted 23.976 -> 25 fps style drift (x 25/23.976)
  es.noisy.srt            Spanish with credits, an advert, lyrics, sound labels,
                          speaker labels and filler-only cues added
  es.ass                  Spanish as Advanced SubStation with override tags,
                          a Sign-style cue and a Comment line
  es.cp1252.srt           Spanish saved in Windows-1252 instead of UTF-8
  truth.json              cue list with timings, used by the checks
Run:  python -I testbed/make_fixtures.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "umbrella-weather")


def load_script():
    rows = []
    with open(os.path.join(FIX, "script.tsv"), encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            rows.append(dict(zip(header, line.split("\t"))))
    return rows


def assign_times(rows):
    t = 4.0
    prev_scene = rows[0]["scene"]
    cues = []
    for i, r in enumerate(rows):
        if r["scene"] != prev_scene:
            t += 7.0
            prev_scene = r["scene"]
        dur = min(max(1.4 + 0.055 * len(r["es"]), 1.6), 4.2)
        start, end = round(t, 3), round(t + dur, 3)
        cues.append({"n": i + 1, "scene": int(r["scene"]), "speaker": r["speaker"],
                     "start": start, "end": end, "es": r["es"], "en": r["en"]})
        t = end + 0.7 + (i % 3) * 0.25
    return cues


def ts_srt(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ts_ass(sec):
    cs = int(round(sec * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def write_srt(path, items, encoding="utf-8"):
    out = []
    for k, (start, end, text) in enumerate(items, 1):
        out.append(f"{k}\n{ts_srt(start)} --> {ts_srt(end)}\n{text}\n")
    with open(path, "w", encoding=encoding, newline="\n") as f:
        f.write("\n".join(out))


def main():
    rows = load_script()
    cues = assign_times(rows)
    es = [(c["start"], c["end"], c["es"]) for c in cues]
    en = [(c["start"], c["end"], c["en"]) for c in cues]
    write_srt(os.path.join(FIX, "es.srt"), es)
    write_srt(os.path.join(FIX, "en.srt"), en)
    write_srt(os.path.join(FIX, "en.shift4.srt"), [(s + 4.0, e + 4.0, t) for s, e, t in en])
    k = 25 / 23.976
    write_srt(os.path.join(FIX, "en.drift.srt"), [(s * k, e * k, t) for s, e, t in en])
    write_srt(os.path.join(FIX, "es.cp1252.srt"), es, encoding="cp1252")

    # Noisy Spanish: noise cues placed in the opening and in the 7-second scene breaks,
    # speaker labels added to three dialogue cues.
    noisy = list(es)
    labelled = {9: "MARCO: ", 21: "MARCO: ", 97: "MARCO: "}  # 0-based indexes of cues 10, 22, 98
    noisy = [(s, e, labelled.get(i, "") + t) for i, (s, e, t) in enumerate(noisy)]
    breaks = []
    for a, b in zip(cues, cues[1:]):
        if b["scene"] != a["scene"]:
            breaks.append((a["end"], b["start"]))
    noise_in_breaks = [
        ["♪ Llueve sobre la ciudad ♪", "Mmm."],
        ["[Suena el teléfono]", "Eh..."],
        ["(Risas)", "Ajá."],
        ["[Llueve con fuerza]", "¡Lena!"],
    ]
    extra = [(0.5, 3.4, "Subtítulos: Equipo Paraguas")]
    for (gs, ge), texts in zip(breaks, noise_in_breaks):
        extra.append((gs + 0.8, gs + 3.0, texts[0]))
        extra.append((gs + 3.6, gs + 5.6, texts[1]))
    last_end = cues[-1]["end"]
    extra.append((last_end + 1.0, last_end + 4.0, "Descarga más subtítulos en www.subtitulos-ejemplo.test"))
    noisy = sorted(noisy + extra)
    write_srt(os.path.join(FIX, "es.noisy.srt"), noisy)

    # Advanced SubStation version of the Spanish file.
    ass = [
        "[Script Info]",
        "Title: Umbrella Weather",
        "ScriptType: v4.00+",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, Bold, Italic, Alignment, MarginL, MarginR, MarginV",
        "Style: Default,Arial,48,&H00FFFFFF,0,0,2,20,20,30",
        "Style: Sign,Arial,40,&H0000FFFF,1,0,8,20,20,30",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        "Comment: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,Timing checked against the 2026 cut",
    ]
    for i, c in enumerate(cues):
        text = c["es"]
        if i % 7 == 0:
            text = "{\\i1}" + text + "{\\i0}"
        if i % 11 == 5 and ". " in text:
            text = text.replace(". ", ".\\N", 1)
        ass.append(f"Dialogue: 0,{ts_ass(c['start'])},{ts_ass(c['end'])},Default,{c['speaker']},0,0,0,,{text}")
        if i == 33:  # cue 34 "Sale del andén cuatro." -> add an on-screen sign
            ass.append(f"Dialogue: 0,{ts_ass(c['start'])},{ts_ass(c['end'])},Sign,,0,0,0,,{{\\pos(960,80)}}ANDÉN 4")
    with open(os.path.join(FIX, "es.ass"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(ass) + "\n")

    with open(os.path.join(FIX, "truth.json"), "w", encoding="utf-8") as f:
        json.dump({"title": "Umbrella Weather", "year": 2026, "cues": cues,
                   "noise_texts": [t for _, _, t in extra],
                   "labelled_cues": [i + 1 for i in labelled]}, f, ensure_ascii=False, indent=1)
    print(f"{len(cues)} cues, last ends at {ts_srt(cues[-1]['end'])}; files written to {FIX}")


if __name__ == "__main__":
    sys.exit(main())
