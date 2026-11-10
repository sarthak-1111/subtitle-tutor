# Off-device test bench (PC stand-in, not the NAS)

This folder tests the Subtitle Tutor Skill before it can run on a UGREEN NAS. It is **not** part of the Skill package: the package is only the `subtitle-tutor/` folder with Markdown files. Nothing here is installed on the NAS.

What it shows: whether a capable model, given only `SKILL.md` and its references, follows the workflow, asks before every write, uses the experts' real results, and produces a sheet whose phrases, timestamps and translations match the subtitles. What it cannot show: how the real NAS assistant, its model and the real experts behave. Those results will be measured on the finalist test device.

## Parts

| File | What it does |
|---|---|
| `fixtures/umbrella-weather/script.tsv` | "Umbrella Weather", an original 136-line Spanish and English screenplay written for these tests (CC0): a café, a station, a flat viewing, a pharmacy and a dinner. |
| `make_fixtures.py` | Builds the subtitle files from the script: an aligned pair, English shifted by 4.0 s, English with frame-rate drift, a noisy Spanish file (credits, an advert, lyrics, sound labels, fillers, speaker labels), an `.ass` version with override tags and a sign, a Windows-1252 copy, and `truth.json` with every cue. |
| `emulator.py` | Runs one scenario. A local model served by Ollama plays the NAS assistant with `SKILL.md` and the references as its instructions, and sends each delegate command through a `delegate` tool call. The script plays the four NAS experts on a virtual NAS folder, the NAS approval prompt, and the user with scripted answers. It writes `runs/<scenario>/transcript.md`, `events.json` and the saved files. |
| `checks.py` | Scores every run against `truth.json` and the event log, then writes `RESULTS.md`. |
| `runs/` | Transcripts, event logs, saved sheets and scores of the runs reported in `RESULTS.md`; `runs/dev/` holds the earlier runs described in `DEVLOG.md`. |
| `DEVLOG.md` | What the earlier runs found and how the Skill text and the harness were changed. |

All six Skill files, including `references/example-sheet.md`, go into the model's instructions unchanged. The example sheet uses a different script ("Quay Three", French), so the model cannot copy answers from it.

## Scenarios

| Scenario | Situation | What must happen |
|---|---|---|
| `core` | Aligned Spanish and English files. The user says "yes with flashcards", agrees to the tag, then asks to replay phrase 3. | 20 phrases copied exactly from the Spanish cues, English lines paired by time, quiz of 10, flashcards, tag; the replay gives a timestamp without starting playback. |
| `offset` | The English file starts 4.0 s late. | The constant offset is found, reported and corrected. |
| `drift` | The English file comes from a 25 fps release; the gap grows from 0.2 s to 23 s. | "Misaligned" is reported; no subtitle pairing; the user's choice (NAS translation) is used. |
| `download` | No Spanish file on the NAS. | The Skill asks before the online search, shows candidates, downloads only the chosen file, and finds it by listing the folder again. |
| `notfound` | The user asks for a title that is not in the library. | One search, a clear "not found", no substitute title, nothing else. |
| `decline` | The user says no to saving. | Nothing is written; the sheet is shown in the conversation. |
| `noisy` | The Spanish file has credits, an advert, lyrics, sound labels, fillers and speaker labels. | None of them reach the sheet. |
| `ass` | The Spanish file is Advanced SubStation, advanced level, 15 phrases. | Override tags, the sign cue and the comment line are ignored. |
| `repeat` | A sheet from an earlier lesson is in the lesson folder. | It is found; no phrase is repeated; 1 to 3 review questions; the old sheet is not replaced. |
| `unsupported` | No English file, the user declines the online search, and translation reports an unsupported pair. | The pair is reported, no translation is invented, and phrases are marked "no translation available". |

## Run it

Requirements: Python 3.10 or later and [Ollama](https://ollama.com) with an instruction-following model. The runs in `RESULTS.md` used `gpt-oss:120b` with high reasoning; `DEVLOG.md` describes the earlier runs, first with medium and then with high reasoning.

```text
python -I testbed/make_fixtures.py
python -I testbed/emulator.py --scenario core --think high
python -I testbed/emulator.py --scenario repeat --think high      (uses the sheet saved by the core run)
python -I -X utf8 testbed/checks.py
```

`--model NAME` picks another Ollama model, `--think low|medium|high|none` sets the reasoning effort, `--num-ctx N` sets the context size, and `--protocol text` makes the model write delegate commands as text instead of calling the `delegate` tool.

## Limits

- The emulated experts follow the public capability catalog; the real experts may phrase results differently, ask their own questions, or need different approvals.
- The emulated user answers by simple rules, so each run follows one path through the Skill.
- The model on the NAS is not known in advance and may be smaller than the stand-in model.
- The model's reasoning from earlier turns is not passed back to it, as in most agent runtimes. Whether the NAS assistant keeps it is not known.
- One original short screenplay (about 9 minutes) is used. Real films have 1,000 to 2,000 cues; the Skill's block-wise rule for long files is not exercised here.
