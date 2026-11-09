"""Off-device stand-in run of the subtitle-tutor Skill.

A local model (served by Ollama) plays the NAS assistant and follows subtitle-tutor/SKILL.md and
its references word for word. This harness plays everything else:
  * the NAS experts (media-agent, file-agent, document-agent, knowledge-agent), acting on a
    virtual NAS folder built from the test fixtures for each scenario;
  * the NAS approval prompt for state-changing actions (approved in these scenarios);
  * the user, with scripted answers chosen by simple rules.
Every model reply, delegation and answer is logged; checks.py scores the run afterwards.

This is NOT the UGREEN NAS and NOT the real experts. Expert behaviour is inferred from the public
capability catalog. Python standard library only. Not part of the Skill package.

Usage:  python -I testbed/emulator.py --scenario core [--model gpt-oss:120b] [--run-id NAME]
"""
import argparse
import datetime
import glob
import json
import os
import re
import shutil
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SKILL = os.path.join(REPO, "subtitle-tutor")
FIX = os.path.join(HERE, "fixtures", "umbrella-weather")
RUNS = os.path.join(HERE, "runs")
OLLAMA = "http://127.0.0.1:11434/api/chat"

MOVIE_DIR = "/volume1/Movies/Umbrella Weather (2026)"
VIDEO = MOVIE_DIR + "/Umbrella Weather (2026).mkv"
HOME = "/volume1/home/demo"
LESSONS = HOME + "/Language Lessons/Umbrella Weather"
TODAY = datetime.date.today()

ADAPTER_TEXT = f"""You are the NAS assistant on a UGREEN AI NAS, running the Skill below for the user.

How this environment works:
- To hand a task to a NAS expert, write the delegate command from the Skill on its own line at the end of your reply: delegate --target AGENT --instruction '...' . Replace every {{VALUE}} in it with its real value first. At most one delegate command per reply. A short note for the user may come before it.
- The expert's result comes back in the next message, which starts with [delegation result].
- A reply without a delegate command is a message to the user. The user's answer comes back in the next message, which starts with [user].
- When the task is finished or stopped, end your last message to the user with the line END OF TASK.
Today's date is {TODAY.isoformat()}.
"""

ADAPTER_TOOLS = f"""You are the NAS assistant on a UGREEN AI NAS, running the Skill below for the user.

How this environment works:
- A delegate command in the Skill, delegate --target AGENT --instruction '...', is sent by calling the tool `delegate` with `target` set to AGENT and `instruction` set to the text inside the single quotes, with every {{VALUE}} replaced by its real value.
- The tool returns the expert's result. A NAS approval prompt may make a result arrive later, in a message that starts with [delegation result].
- A reply without a tool call is a message to the user. The user's answer comes back in the next message, which starts with [user].
- When the task is finished or stopped, end your last message to the user with the line END OF TASK.
Today's date is {TODAY.isoformat()}.
"""

DELEGATE_TOOL = {"type": "function", "function": {
    "name": "delegate",
    "description": "Send one task to a registered NAS expert and return its result.",
    "parameters": {"type": "object", "required": ["target", "instruction"], "properties": {
        "target": {"type": "string", "description": "Expert ID, for example media-agent or file-agent."},
        "instruction": {"type": "string", "description": "The complete, self-contained instruction text."}}}}}

INTERMEDIATE = "Make an intermediate Spanish lesson from Umbrella Weather. My language is English."
SCENARIOS = {
    "core": dict(request=INTERMEDIATE, files={"es": "es.srt", "en": "en.srt"}, save="Yes with flashcards.",
                 tag="Yes.", followups=["Replay phrase 3."],
                 about="Aligned Spanish and English files; save with flashcards; tag; replay request."),
    "offset": dict(request=INTERMEDIATE, files={"es": "es.srt", "en": "en.shift4.srt"}, save="Yes.", tag="No.",
                   about="English file starts 4.0 s late (constant offset)."),
    "drift": dict(request="Make an intermediate Spanish lesson from Umbrella Weather, 12 phrases. My language is English.",
                  files={"es": "es.srt", "en": "en.drift.srt"}, save="Yes.", tag="No.",
                  misaligned_choice="Translate the phrases with the NAS translation, please.",
                  about="English file from a 25 fps release: the gap grows from 0.2 s to 23 s (drift)."),
    "download": dict(request="Make a beginner Spanish lesson from Umbrella Weather with 10 phrases. I speak English.",
                     files={"en": "en.srt"}, online={"es": "es.srt"}, save="Yes.", tag="No.",
                     about="No Spanish file on the NAS; user agrees to the online search and download."),
    "notfound": dict(request="Make a French lesson from Casablanca. I speak English.",
                     files={"es": "es.srt", "en": "en.srt"}, save="Yes.", tag="No.",
                     about="Title not in the library: must stop without offering another title."),
    "decline": dict(request=INTERMEDIATE, files={"es": "es.srt", "en": "en.srt"}, save="No.", tag="No.",
                    about="User says no to saving: nothing may be written."),
    "noisy": dict(request=INTERMEDIATE, files={"es": "es.noisy.srt", "en": "en.srt"}, save="Yes.", tag="No.",
                  about="Spanish file with credits, an advert, lyrics, sound labels, fillers and speaker labels."),
    "ass": dict(request="Make an advanced Spanish lesson from Umbrella Weather, 15 phrases. My language is English.",
                files={"es": "es.ass", "en": "en.srt"}, save="Yes.", tag="No.",
                about="Spanish as Advanced SubStation with override tags, a sign cue and a comment line."),
    "repeat": dict(request="Make another intermediate Spanish lesson from Umbrella Weather. My language is English.",
                   files={"es": "es.srt", "en": "en.srt"}, save="Yes.", tag="No.", earlier_sheet=True,
                   about="An earlier sheet exists: no repeated phrases, review questions, no overwrite."),
    "unsupported": dict(request="Make a beginner Spanish lesson from Umbrella Weather with 10 phrases. My language is English.",
                        files={"es": "es.srt"}, online={}, save="Yes.", tag="No.", translate_fails=True,
                        decline_download=True,
                        about="No English file, online search declined, translation pair unsupported."),
}
SUB_NAMES = {"es.srt": "Umbrella Weather (2026).es.srt", "es.noisy.srt": "Umbrella Weather (2026).es.srt",
             "es.ass": "Umbrella Weather (2026).es.ass", "es.cp1252.srt": "Umbrella Weather (2026).es.srt",
             "en.srt": "Umbrella Weather (2026).en.srt", "en.shift4.srt": "Umbrella Weather (2026).en.srt",
             "en.drift.srt": "Umbrella Weather (2026).en.srt"}
LANG_NAMES = {"es": "spanish", "en": "english"}
DELEG = re.compile(r"delegate\s+--target\s+([A-Za-z0-9_-]+)\s+--instruction\s+(['\"])", re.S)
ESC = "'\"'\"'"
# Requests for an answer that carry no question mark.
ASK = re.compile(r"please (reply|confirm|choose|answer)|reply \**[\"“]?yes|let me know (whether|if you want|which)", re.I)
# Reference files left out of the prompt (none: example-sheet.md uses a different script).
LEFT_OUT = set()


def clock():
    return datetime.datetime.now().strftime("%H:%M:%S")


class Run:
    def __init__(self, scenario, model, run_id, think, num_ctx, earlier_sheet=None, protocol="tools"):
        self.protocol = protocol
        self.name = scenario
        self.cfg = SCENARIOS[scenario]
        self.model, self.think, self.num_ctx = model, think, num_ctx
        self.dir = os.path.join(RUNS, run_id)
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        self.nas = os.path.join(self.dir, "nas")
        os.makedirs(self.local(MOVIE_DIR))
        os.makedirs(self.local(HOME + "/Notes"))
        open(self.local(VIDEO), "wb").close()
        for fname in self.cfg["files"].values():
            shutil.copy(os.path.join(FIX, fname), self.local(MOVIE_DIR + "/" + SUB_NAMES[fname]))
        self.earlier = None
        if self.cfg.get("earlier_sheet"):
            src = earlier_sheet or self.find_core_sheet()
            old_date = (TODAY - datetime.timedelta(days=7)).isoformat()
            text = open(src, encoding="utf-8").read()
            text = re.sub(r"(\|\s*Made on\s*\|\s*)\d{4}-\d{2}-\d{2}", r"\g<1>" + old_date, text)
            os.makedirs(self.local(LESSONS))
            self.earlier = f"Umbrella Weather - Spanish intermediate - {old_date}.md"
            with open(os.path.join(self.local(LESSONS), self.earlier), "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
        self.tags = {}
        self.log = []          # (speaker, text) transcript entries
        self.events = []       # structured events for checks.py
        self.thinking = []
        self.pending = []      # expert results held back while the NAS approval prompt is open
        self.idle = 0          # consecutive messages to the user that ask nothing
        self.flags = {}

    @staticmethod
    def find_core_sheet():
        found = [p for p in glob.glob(os.path.join(RUNS, "core*", "output", "**", "*.md"), recursive=True)]
        if not found:
            raise SystemExit("repeat needs a sheet from a core run first (or --earlier-sheet PATH)")
        return max(found, key=os.path.getmtime)

    # ---------- virtual NAS ----------
    def local(self, vpath):
        vpath = vpath.strip().strip("'\"`").rstrip("/")
        return os.path.join(self.nas, vpath.lstrip("/").replace("/", os.sep))

    def vlist(self, vdir):
        p = self.local(vdir)
        if not os.path.isdir(p):
            return None
        out = []
        for n in sorted(os.listdir(p)):
            fp = os.path.join(p, n)
            st = os.stat(fp)
            out.append({"name": n, "path": vdir.strip().rstrip("/") + "/" + n,
                        "type": "folder" if os.path.isdir(fp) else "file", "size": st.st_size,
                        "modified": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")})
        return out

    # ---------- model ----------
    def ollama(self, messages, think=None, extra=None, tools=None):
        body = {"model": self.model, "messages": messages, "stream": False, "options": {"seed": 7}}
        if self.num_ctx:
            body["options"]["num_ctx"] = self.num_ctx
        if think:
            body["think"] = think
        if tools:
            body["tools"] = tools
        body["options"].update(extra or {})
        req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3600) as r:
            return json.load(r)

    def chat(self, messages):
        """Return (content, tool_calls, raw assistant message)."""
        t0 = time.time()
        tools = [DELEGATE_TOOL] if self.protocol == "tools" else None
        data = self.ollama(messages, self.think, {"num_predict": 40000}, tools)
        msg = data["message"]
        self.thinking.append(msg.get("thinking", ""))
        self.events.append({"kind": "model_turn", "seconds": round(time.time() - t0, 1),
                            "eval_count": data.get("eval_count"), "prompt_eval_count": data.get("prompt_eval_count")})
        calls = []
        for c in msg.get("tool_calls") or []:
            fn = c.get("function", {})
            args = fn.get("arguments") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = {"instruction": args}
            calls.append((fn.get("name", ""), str(args.get("target", "")), str(args.get("instruction", ""))))
        assistant = {"role": "assistant", "content": msg.get("content", "")}
        if msg.get("tool_calls"):
            assistant["tool_calls"] = msg["tool_calls"]
        return msg.get("content", ""), calls, assistant

    def translate(self, lines):
        prompt = [{"role": "system", "content": "You are a translation service. Translate each numbered line from Spanish into English. Reply with the numbered translations only, one per line, keeping the numbers."},
                  {"role": "user", "content": lines}]
        data = self.ollama(prompt, "low" if self.think else None, {"temperature": 0})
        return data["message"]["content"].strip()

    # ---------- emulated experts ----------
    def expert(self, target, ins):
        low = ins.lower()
        ev = {"kind": "delegate", "target": target, "instruction": ins if len(ins) < 6000 else ins[:6000] + " [...]"}
        self.events.append(ev)

        def done(data):
            ev["status"] = "completed"
            return {"status": "completed", "data": data}

        def fail(msg):
            ev["status"] = "failed"
            return {"status": "failed", "error": msg}

        if target == "media-agent":
            if "most recently" in low:
                ev["action"] = "recent"
                y = (TODAY - datetime.timedelta(days=1)).isoformat()
                return done({"items": [{"title": "Umbrella Weather", "year": 2026, "type": "movie", "media_id": "m-2001",
                                        "path": VIDEO, "last_watched": y + " 21:40"}]})
            m = re.search(r"whose title matches (.+?)\.\s*read only", ins, re.I | re.S)
            if m and "search the nas video library" in low:
                ev["action"] = "search"
                q = re.sub(r"[^a-z0-9 ]", "", m.group(1).lower()).strip()
                hit = bool(q) and (q in "umbrella weather" or "umbrella weather" in q)
                items = [{"title": "Umbrella Weather", "year": 2026, "type": "movie", "media_id": "m-2001",
                          "path": VIDEO}] if hit else []
                return done({"items": items, "note": "" if hit else "no results"})
            if "search online subtitles" in low:
                ev["action"] = "subtitle-search"
                cands = []
                for lang in self.cfg.get("online", {}):
                    if f"({lang})" in low or LANG_NAMES[lang] in low:
                        cands = [{"file-id": 7781, "file_name": "Umbrella.Weather.2026.1080p.WEB.spa.srt", "language": "Spanish",
                                  "format": "srt", "release": "Umbrella.Weather.2026.1080p.WEB"},
                                 {"file-id": 7782, "file_name": "Umbrella.Weather.2026.DVDRip.spa.srt", "language": "Spanish",
                                  "format": "srt", "release": "Umbrella.Weather.2026.DVDRip"}]
                return done({"candidates": cands, "note": "" if cands else "no results"})
            if "download the subtitle" in low and re.search(r"file-id \d+", ins):
                ev["action"] = "subtitle-download"
                fname = self.cfg.get("online", {}).get("es")
                if not fname:
                    return fail("subtitle not available")
                shutil.copy(os.path.join(FIX, fname), self.local(MOVIE_DIR + "/Umbrella Weather (2026).spa.srt"))
                return self.approval("subtitle download from an online source", done({"download": "finished"}))
            if "start playback" in low:
                ev["action"] = "play"
                return done({"playback": "started", "player": "UGREEN Video app, Living Room TV"})
        if target == "file-agent":
            m = re.search(r"list the files directly inside the folder (.+?),? without going into subfolders", ins, re.I | re.S)
            if m:
                ev["action"] = "ls"
                items = self.vlist(m.group(1))
                if items is None:
                    return fail("folder not found: " + m.group(1).strip())
                subs = [i for i in items if re.search(r"\.(srt|ass|ssa)$", i["name"], re.I)]
                data = {"folder": m.group(1).strip(), "files": subs, "note": "" if subs else "no results"}
                if "tags currently attached" in low:
                    data["video_tags"] = self.tags.get(VIDEO, [])
                return done(data)
            m = re.search(r"read the first (\d+) bytes of the text file (.+?) and return", ins, re.I | re.S)
            if m:
                ev["action"] = "cat-head"
                p = self.local(m.group(2))
                if not os.path.isfile(p):
                    return fail("file not found: " + m.group(2).strip())
                return done({"content": open(p, "rb").read(int(m.group(1))).decode("utf-8", "replace")})
            m = re.search(r"read the (?:whole )?text file (.+?) and return", ins, re.I | re.S)
            if m:
                ev["action"] = "cat"
                ev["path"] = m.group(1).strip()
                p = self.local(m.group(1))
                if not os.path.isfile(p):
                    return fail("file not found: " + m.group(1).strip())
                raw = open(p, "rb").read()
                chunks = [raw[i:i + 65536].decode("utf-8", "replace") for i in range(0, len(raw), 65536)] or [""]
                return done({"path": m.group(1).strip(), "total_bytes": len(raw), "chunks": chunks})
            if "personal folder of the current user" in low:
                ev["action"] = "get-user-dir"
                return done({"path": HOME})
            m = re.search(r"check whether the folder (.+?) exists", ins, re.I | re.S)
            if m:
                ev["action"] = "stat-dir"
                items = self.vlist(m.group(1))
                return done({"exists": items is not None, "files": items or [],
                             "note": "the folder does not exist" if items is None else ("the folder is empty" if not items else "")})
            m = re.search(r"create the folder (.+?), including", ins, re.I | re.S)
            if m:
                ev["action"] = "mkdir"
                os.makedirs(self.local(m.group(1)), exist_ok=True)
                return self.approval("create folder " + m.group(1).strip(), done({"path": m.group(1).strip()}))
            m = re.search(r"check whether a file named (.+?) exists in the folder (.+?)\.\s*read only", ins, re.I | re.S)
            if m:
                ev["action"] = "stat-file"
                p = os.path.join(self.local(m.group(2)), m.group(1).strip())
                return done({"exists": os.path.exists(p)})
            m = re.search(r"check whether the file (.+?) exists", ins, re.I | re.S)
            if m:
                ev["action"] = "stat"
                return done({"exists": os.path.exists(self.local(m.group(1)))})
            m = re.search(r"attach the tag named (.+?) to the video file (.+?)\.\s*the user", ins, re.I | re.S)
            if m:
                ev["action"] = "tag"
                self.tags.setdefault(m.group(2).strip(), []).append(m.group(1).strip())
                return self.approval("add the tag " + m.group(1).strip(), done({"tag_id": 41, "attached": True}))
        if target == "document-agent" and "translate the following numbered lines" in low:
            ev["action"] = "translate"
            if self.cfg.get("translate_fails"):
                return self.approval("translation", fail("language pair not supported: es to en is not available on this NAS"))
            out = self.translate(ins.split("Lines:", 1)[-1].strip())
            return self.approval("translation", done({"mode": "inline", "translation": out}))
        if target == "knowledge-agent" and re.search(r"save the following (markdown|plain) text", low):
            ev["action"] = "save"
            m = re.search(r"(?:new file named|as the file) (.+?) in the folder (.+?)(?:,| replacing|\.\s*the user)", ins, re.I | re.S)
            if not m:
                return fail("could not read the file name and folder from the instruction")
            name, folder = m.group(1).strip(), m.group(2).strip()
            text = ins.split("Text:", 1)[-1].lstrip("\n ")
            if not os.path.isdir(self.local(folder)):
                return fail("folder does not exist: " + folder)
            p = os.path.join(self.local(folder), name)
            if os.path.exists(p) and "replacing the existing file" not in low:
                return fail("a file with this name already exists")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            ev["saved"] = folder + "/" + name
            return self.approval("save " + name, done({"verified": True, "output_file": folder + "/" + name,
                                                         "bytes": len(text.encode("utf-8"))}))
        ev["action"] = "unknown"
        return fail("the emulated expert did not recognise this instruction")

    def approval(self, what, result):
        """Emulate the NAS approval prompt: waiting_approval now, the result after the user approves."""
        self.pending.append(result)
        self.events.append({"kind": "approval", "what": what})
        return {"status": "waiting_approval", "message": f"The NAS is asking the user to approve: {what}."}

    # ---------- emulated user ----------
    def answer(self, key, text):
        self.flags.setdefault(key, text)
        return text

    def user_reply(self, text):
        """Scripted user. Each topic always gets the same answer, however often it is asked."""
        low = text.lower()
        c = self.cfg
        ask = "?" in text or bool(ASK.search(low))
        if not ask:
            return "OK."
        # The save question of step 7 has priority: it may also mention untranslated phrases or the tag.
        if re.search(r"save the (study )?sheet|yes with flashcards", low):
            return self.answer("save_answer", c["save"])
        if "misaligned" in low:
            return self.answer("misaligned_answer", c.get("misaligned_choice", "Stop, please."))
        if re.search(r"file-id|candidates?\b|which (one|subtitle|file)|pick one", low) and "download" in low:
            return self.answer("download_answer", "The first one, please. Yes, download it.")
        if re.search(r"(search|look) for .{0,40}subtitles? online|search online|online (subtitle )?search", low):
            return self.answer("search_answer", "No, don't search online." if c.get("decline_download") else "Yes, go ahead.")
        if re.search(r"without (a |any )?translations?|no translation available|untranslated", low):
            return self.answer("untranslated_answer", "Save it with the phrases marked as untranslated, please.")
        if re.search(r"\btag", low):
            return self.answer("tag_answer", c["tag"])
        if re.search(r"\bsave\b|\bstore\b|write the (study )?sheet", low):
            return self.answer("save_answer", c["save"])
        if re.search(r"start (the )?(title|film|movie|video|playback)|play (it|the)|open the (film|video)", low):
            return self.answer("play_answer", "No, thanks. The timestamp is enough.")
        if "encoding" in low:
            return "Continue with the readable lines."
        return "Yes."

    # ---------- main loop ----------
    def run(self, max_turns=45):
        adapter = ADAPTER_TOOLS if self.protocol == "tools" else ADAPTER_TEXT
        system = adapter + "\n\n===== SKILL.md =====\n" + open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read()
        for f in sorted(os.listdir(os.path.join(SKILL, "references"))):
            if f in LEFT_OUT:
                continue
            system += f"\n\n===== references/{f} =====\n" + open(os.path.join(SKILL, "references", f), encoding="utf-8").read()
        messages = [{"role": "system", "content": system}, {"role": "user", "content": "[user] " + self.cfg["request"]}]
        self.log.append(("user", self.cfg["request"]))
        followups = list(self.cfg.get("followups", []))
        for turn in range(max_turns):
            out, calls, assistant = self.chat(messages)
            if not out.strip() and not calls:
                # Reasoning used the whole output budget and nothing was said: ask the model once more.
                self.events.append({"kind": "harness_note", "what": "empty reply; regenerated once"})
                out, calls, assistant = self.chat(messages)
            messages.append(assistant)
            shown = out + "".join(f"\n[tool call] delegate --target {t} --instruction '{i}'" for _, t, i in calls)
            self.log.append(("assistant", shown))
            print(f"[{clock()}] turn {turn + 1} ({self.events[-1]['seconds']}s): {shown.strip()[:100]!r}", flush=True)
            if calls:
                self.idle = 0
                if out.strip():
                    self.events.append({"kind": "to_user", "text": out.strip(), "with_delegate": True})
                if len(calls) > 1:
                    self.events.append({"kind": "protocol_warning", "what": "more than one delegate command in one reply"})
                for name, target, ins in calls:
                    if name != "delegate":
                        res = {"status": "failed", "error": f"unknown tool {name}"}
                    else:
                        if "'" in ins:
                            self.events.append({"kind": "protocol_warning", "what": "straight single quote in an instruction"})
                        if self.pending:
                            self.events.append({"kind": "protocol_warning", "what": "new delegate sent while an approval was still open"})
                        res = self.expert(target, ins.strip())
                    payload = json.dumps(res, ensure_ascii=False)
                    messages.append({"role": "tool", "content": payload, "tool_name": "delegate"})
                    self.log.append(("expert", payload))
                continue
            m = DELEG.search(out)
            if m and self.protocol == "tools":
                self.events.append({"kind": "protocol_warning", "what": "delegate command written as text instead of a tool call"})
            if m:
                pre = out[:m.start()].strip().strip("`").strip()
                if pre:
                    self.events.append({"kind": "to_user", "text": pre, "with_delegate": True})
                found = list(DELEG.finditer(out))
                if len(found) > 1:
                    # Executed in order, like several tool calls in one turn, but counted as a deviation.
                    self.events.append({"kind": "protocol_warning", "what": "more than one delegate command in one reply"})
                results = []
                for k, d in enumerate(found):
                    rest = out[d.end(): found[k + 1].start() if k + 1 < len(found) else len(out)]
                    end = rest.rfind(d.group(2))
                    ins = rest[:end] if end >= 0 else rest
                    if d.group(2) == "'":
                        unescaped = ins.count("'") - 3 * ins.count(ESC)
                        if unescaped:
                            self.events.append({"kind": "protocol_warning", "what": f"{unescaped} unescaped single quote(s) in an instruction"})
                        ins = ins.replace(ESC, "'")
                    if self.pending:
                        self.events.append({"kind": "protocol_warning", "what": "new delegate sent while an approval was still open"})
                    results.append(self.expert(d.group(1), ins.strip()))
                payload = "\n".join("[delegation result] " + json.dumps(r, ensure_ascii=False) for r in results)
                messages.append({"role": "user", "content": payload})
                self.log.append(("expert", payload))
                continue
            self.events.append({"kind": "to_user", "text": out})
            body = out.replace("END OF TASK", "").strip().rstrip(".").strip()
            tail = "\n\n".join(body.split("\n\n")[-2:]) if body else ""
            open_question = "?" in tail or bool(ASK.search(tail))
            if "END OF TASK" in out and open_question:
                # A question was asked in the same message: answer it instead of ending the run.
                self.events.append({"kind": "harness_note", "what": "END OF TASK after an open question"})
            elif "END OF TASK" in out:
                if followups:
                    f = followups.pop(0)
                    self.events.append({"kind": "user_followup", "text": f})
                    messages.append({"role": "user", "content": "[user] " + f})
                    self.log.append(("user", f))
                    continue
                self.events.append({"kind": "end"})
                break
            quiet = not self.pending and not open_question and "END OF TASK" not in out \
                and not ASK.search(out)
            self.idle = self.idle + 1 if quiet else 0
            if self.idle >= 2:
                # Two messages in a row with nothing asked and nothing pending: a real user would stop here.
                self.idle = 0
                self.events.append({"kind": "harness_note", "what": "conversation ended without END OF TASK"})
                if followups:
                    f = followups.pop(0)
                    self.events.append({"kind": "user_followup", "text": f})
                    messages.append({"role": "user", "content": "[user] " + f})
                    self.log.append(("user", f))
                    continue
                self.events.append({"kind": "end"})
                break
            if self.pending:
                parts = ["[user] I approved it in the NAS app."]
                parts += ["[delegation result] " + json.dumps(r, ensure_ascii=False) for r in self.pending]
                self.pending = []
                self.events.append({"kind": "approval_given"})
                messages.append({"role": "user", "content": "\n".join(parts)})
                self.log.append(("user + expert", "\n".join(parts)))
                continue
            reply = self.user_reply(out)
            self.events.append({"kind": "user_reply", "text": reply})
            messages.append({"role": "user", "content": "[user] " + reply})
            self.log.append(("user", reply))
        else:
            self.events.append({"kind": "max_turns_reached"})

    def save(self, seconds):
        files = []
        for root, _, names in os.walk(self.nas):
            for n in names:
                files.append("/" + os.path.relpath(os.path.join(root, n), self.nas).replace(os.sep, "/"))
        out_dir = os.path.join(self.dir, "output")
        lessons = self.local(HOME + "/Language Lessons")
        if os.path.isdir(lessons):
            shutil.copytree(lessons, out_dir)
        with open(os.path.join(self.dir, "transcript.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# Stand-in run: {self.name}\n\n{self.cfg['about']}\n\n"
                    f"Model `{self.model}` served by Ollama on a PC, not the NAS. The experts, the approval prompt and "
                    f"the user are emulated by `testbed/emulator.py`. Date {TODAY.isoformat()}.\n\n")
            for who, text in self.log:
                f.write(f"## {who}\n\n````text\n{text}\n````\n\n")
        with open(os.path.join(self.dir, "events.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"scenario": self.name, "model": self.model, "think": self.think, "protocol": self.protocol,
                       "date": TODAY.isoformat(),
                       "seconds": round(seconds), "config": self.cfg, "earlier_sheet": self.earlier,
                       "answers": self.flags, "tags": self.tags, "nas_files_at_end": sorted(files),
                       "events": self.events}, f, ensure_ascii=False, indent=1)
        with open(os.path.join(self.dir, "thinking.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for t in self.thinking:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        shutil.rmtree(self.nas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--think", default="medium", help="reasoning effort for models that support it; 'none' to turn off")
    ap.add_argument("--num-ctx", type=int, default=0, help="context size; 0 keeps the server setting")
    ap.add_argument("--protocol", choices=["tools", "text"], default="tools",
                    help="tools: delegate is a tool call (default); text: delegate commands written in the reply")
    ap.add_argument("--run-id")
    ap.add_argument("--earlier-sheet")
    a = ap.parse_args()
    think = None if a.think == "none" else a.think
    run = Run(a.scenario, a.model, a.run_id or a.scenario, think, a.num_ctx, a.earlier_sheet, a.protocol)
    t0 = time.time()
    try:
        run.run()
    finally:
        run.save(time.time() - t0)
    print(f"done in {time.time() - t0:.0f}s -> {run.dir}")


if __name__ == "__main__":
    main()
