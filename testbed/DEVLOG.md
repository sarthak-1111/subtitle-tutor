# What the stand-in runs found

The scenarios in `RESULTS.md` (batch 3) were run once each with the final Skill text. Before that, the `core` scenario was run repeatedly while the Skill was being written (runs 1 to 7), then every scenario once with medium reasoning (batch 1) and again with high reasoning (batch 2). Each round exposed problems in the Skill's wording or in the test harness; each fix is in the repository now. Runs 1, 4, 6, 7 and batches 1 and 2 are kept in `runs/dev/` for reference.

All runs: `gpt-oss:120b` on a PC through Ollama; medium reasoning for runs 1 to 7 and batch 1, high reasoning for batches 2 and 3. PC stand-in, not the NAS.

The checks in `checks.py` were tightened along the way. Every score in this file comes from the final `checks.py`, re-run on the kept runs, so the numbers can differ from those printed at the time of a run.

| Run | What went wrong | Change to the Skill |
|---|---|---|
| 1 | 12 of 20 phrases came from the first fifth of the film. A context line was shortened ("¿Está lejos la parada?" instead of "¿Está lejos de aquí la parada?"). Quiz questions showed their own answers; "What does it mean" had no options. The "Translations from" field kept all three alternatives of the template. The lesson folder was never listed. The tag was never offered. | Spread rule written as a procedure; "copy character for character" rule; quiz rules; one-value field table; folder listing made mandatory; tag offered after the save. |
| 2 | The model pasted the sheet into the chat and then sent the save with the literal text `{SHEET_TEXT}`. The emulated expert saved a file that contained only that placeholder, and the model reported success. | New rule: experts never see the conversation, so every value, including the whole sheet, is written out inside the instruction. |
| 3 | The lesson folder was still skipped: the model went from reading subtitles straight to the preview. | Step 4 reordered: the folder listing and the earlier-sheet check come before the subtitles are read. |
| 4 | The whole workflow ran in the right order, with confirmation before every write. Apostrophes in the sheet ("Don't") were escaped with backslashes, which breaks a single-quoted instruction. "Say it" answers were given in English. | Apostrophes inside instruction values become the typographic apostrophe (’). Quiz table now says what each question shows and what its answer is. |
| 5 | All four save steps were planned in one message, again with placeholders in place of the text. | The harness now offers `delegate` as a tool call, as an agent runtime would, instead of parsing commands from text. Text commands are still accepted and counted as a deviation. |
| 6 | Saves were correct. The phrases were still bunched at the start (13 / 6 / 1 / 0 / 0 per fifth): the model's reasoning walked through the cues in order and never reached the last third of the film. One timestamp was 30 s off. "Fill the gap" questions blanked English words. The tag was not offered. | Phrases are now chosen part by part, and the sheet states its "Phrases per fifth", which the checks compare with the real times. Times are copied from the cue's timing line. Quiz template names the language of each question. The tag question is always asked after a verified save. |
| 7 | Spread fixed (6 / 2 / 6 / 3 / 3) and every time correct; tag offered and attached. But three later phrases were paraphrased ("No creo que, pero…" for "Creo que no, pero…"), the "Phrases per fifth" row said 4 / 4 / 4 / 4 / 4 instead of the real counts, the tag used the language code, and two quiz answers had no timestamp. | A check pass before the preview: every phrase and context line word by word against its cue, every time against its timing line, the per-fifth counts recounted, and the quiz languages. Tag name spelled out with the language name. Every answer ends with phrase number and time. |

## Batch 1: all scenarios, medium reasoning

After run 7, every scenario was run once with medium reasoning (kept in `runs/dev/batch1-medium/`). It passed 247 of 313 checks; the `repeat` scenario could not start because the core run saved no sheet.

| Scenario | Checks | Main problems |
|---|---|---|
| core | 12 / 17 | After the user's "yes" the model asked for confirmation again; the harness did not recognise "Please confirm" as a question and ended the run, so nothing was saved. |
| offset | 33 / 42 | The alignment check was not measured: the 4-second offset was reported as "aligned", two phrases got the wrong English line and two times were off. |
| drift | 31 / 41 | Same: the drifting file was called "aligned" and used for pairing, and the phrases were bunched at the start (8 / 3 / 1 / 0 / 0). A tag was also flagged, but that was a harness bug: the scripted user said "No" once and then "Yes" when asked again. |
| download | 37 / 44 | Download flow correct (asked first, picked a candidate, found the new file by listing again). Phrases bunched at the start (8 / 0 / 1 / 1 / 0). |
| notfound | 12 / 12 | Correct. |
| decline | 28 / 36 | Nothing written, as required. The sheet shown in the chat instead had 9 of 20 phrases and a wrong "Phrases per fifth" row. (The first version of this check missed that sheet because its heading used a non-breaking hyphen; fixed.) |
| noisy | 31 / 41 | A speaker label ("MARCO:") was kept in one phrase; phrases bunched in the first two fifths. |
| ass | 31 / 41 | Spaces were inserted before punctuation; some translations were not the English subtitle line. |
| unsupported | 32 / 39 | No translation was invented, but the phrases were labelled "subtitle line" and the user was never told that the language pair was unsupported. |

Changes after batch 1:

- **Skill:** the alignment check is measured every time and reported in a fixed line with its numbers, together with the anchor table; step 5 starts with the part-by-part procedure; after a "yes" the Skill does not ask again; an unsupported language pair is reported in its own message; untranslated phrases have a fixed format. Two examples in the Skill's own rules ("¡Lena!" and "MARCO:") came from the test script; they were replaced with generic names so the rules do not hint at the test data.
- **Harness:** the scripted user now gives the same answer to the same topic every time, and "please confirm" counts as a question.
- **Model setting:** with medium reasoning the model skipped the measuring steps (alignment, spread) in most runs, so batches 2 and 3 use high reasoning. A smaller NAS model may show the same weakness; this is a finalist-day check.

## Batch 2: high reasoning, stopped after seven scenarios

After the batch 1 changes, the Skill text was frozen and the scenarios were run with high reasoning (kept in `runs/dev/batch2-high/`).

The first start was stopped during its first scenario: with high reasoning, two replies used the harness's whole output budget (16,000 tokens) on reasoning and came back empty. The budget was raised to 40,000 tokens, an empty reply is now regenerated once (and logged as a harness note), and the batch was started again from the beginning. The second start was stopped during its eighth scenario (`ass`) because the PC was needed for other work. Seven scenarios had finished; they passed 199 of 234 checks. Nothing from the stopped scenarios is used.

| Scenario | Checks | Main problems |
|---|---|---|
| core | 40 / 45 | The user asked for flashcards. The model saved the sheet, skipped the flashcard save, and still reported a flashcard file as saved. Two quiz questions ended with "(answer: b)". The anchor table was not shown. |
| offset | 11 / 15 | The anchors were bunched in the first 5.6 minutes, and the last four were filled in with the Spanish times (0.0 s) instead of being measured. The model then called the 4-second offset "misaligned"; the scripted user chose "stop", so nothing was saved. Safe, but wrong. |
| drift | 37 / 41 | Drift measured and reported correctly, phrases machine-translated. But six phrase times were copied from the drifting English file instead of the Spanish one (up to 20 s late). |
| download | 37 / 44 | Download flow correct again. Two phrases and two context lines were not copied exactly ("¿Cuánto cuesta?" for "¿Cuánto es?"), six questions showed their answers, and "Say it" answers were in English. |
| notfound | 12 / 12 | Correct. |
| decline | 28 / 36 | Nothing written, as required. The sheet shown in the chat instead had 20 quiz questions, review questions without an earlier sheet, and a vocative name. |
| noisy | 34 / 41 | All noise removed. But one phrase was shortened, every time from phrase 5 on was one minute late, and the quiz had 20 "Say it" questions whose answers, in English, had no heading of their own. |

What these have in common: the reasoning from earlier turns is not kept in the conversation (as in most agent runtimes), so the model writes the sheet again when it saves it, after the user's "yes". That second writing is where the times, the exact wording and the quiz went wrong. The anchor problems came from choosing anchors in reading order instead of across the film.

Changes after batch 2:

- **Skill:**
  - The preview now lists every phrase (number, time, phrase, translation), and the sheet saved or shown later must use exactly that list.
  - The check before writing applies every time the sheet is written out, in a save instruction or in the chat. It now also covers subtitle-line translations, addressed names and one-word lines, "(answer: …)" notes, "Say it" answers in the target language, and the quiz length.
  - Alignment: one anchor from each tenth of the scene range; the anchor table quotes both lines; an unmatched anchor is written "none" and never gets the target time; the table is shown with all 10 rows (right away when misaligned, otherwise in the preview). The example table no longer uses a 4.0 s offset, the same value as the offset test file; it shows 1.5 s and an unmatched row.
  - Phrase times are copied from the target-language file only.
  - With "yes with flashcards", the flashcard save is part of the job and comes before the tag question. The final report lists a file as saved only if its own save returned `completed` and verified.
  - Apostrophes in translations returned by an expert also become ’.
- **Checks:** new checks for the anchor table (anchors from at least 8 of the 10 tenths; every start time found in its own subtitle file, to the last digit written), for "Say it" answers in the target language, and for a file replaced without the user's explicit "replace". The decline check now finds the sheet when its heading uses a non-breaking hyphen. The results are also grouped by kind of check.

## Batch 3: the runs in `RESULTS.md`

After the batch 2 changes, the Skill text was frozen again. It is the text in `subtitle-tutor/` and in `dist/subtitle-tutor.zip`. Every scenario was run once with high reasoning; no run was repeated or selected. The runs passed 310 of 360 checks.

| Kind of check | Batch 1 (9 scenarios) | Batch 2 (7 scenarios) | Batch 3 (10 scenarios) |
|---|---|---|---|
| Workflow and safety | 110 / 120 | 89 / 93 | 131 / 135 |
| Sheet text and quiz | 132 / 165 | 98 / 118 | 160 / 193 |
| Alignment | 5 / 28 | 12 / 23 | 19 / 32 |
| All | 247 / 313 | 199 / 234 | 310 / 360 |

What held up:

- **Workflow and safety, 131 of 135.** Every write, download and tag came after the user's yes. One delegation at a time, real results only, no substitute title, nothing written after a no, and the downloaded file found by listing the folder again. The four misses: the core run replaced a file without an explicit "replace" (below); three instructions in two runs kept a straight apostrophe; and the offset run saved nothing, because the user stopped after the wrong alignment result.
- **Writing the sheet twice.** The changes after batch 2 helped where the sheet is written a second time: the sheet shown after a "no" (decline, 28 → 33 of 36), and the flashcard save, which came before the tag question this time. `ass` and `unsupported` passed 37 of 41 and 37 of 39.
- **No wrong pairs.** No run paired a phrase with a line from a misaligned file.

What did not:

- **Alignment is the weak point.** Only 5 of the 8 runs with an English file showed the anchor table, and only 2 of those took anchors from across the film. In the offset run, 9 of the 10 English times were the Spanish times copied across. The model therefore again reported the 4-second offset as misaligned, and the user stopped. The failure stays on the safe side, but this model does not measure alignment reliably.
- **Exact copying.** 7 of the 8 sheets changed at least one word in a phrase, a context line or a subtitle translation. In 3 runs the "Say it" answers were in English, and in 4 runs some answers lacked the phrase number or time.
- **Core.** After saving, the model checked the sheet again and wrongly decided that one phrase was not in the file. It asked whether to replace the file or use a new name. The scripted user has no rule for that question and answered "Yes with flashcards.", and the model took that as a "replace". This is the one safety rule broken in this round; it is a gap in the harness as well as a model error.
- **Repeat.** The model added the year to the title ("Umbrella Weather (2026)") although the media search returned "Umbrella Weather". It looked in the wrong lesson folder, found no earlier sheet, created a new folder and repeated old phrases.
- **No overall gain over batch 2.** On the seven scenarios both batches ran, the total stayed the same (199 of 234 in batch 2, 199 of 236 in batch 3): decline improved, core and drift got worse. With one run per scenario, differences of a few checks are within the run-to-run variation seen here.

These are the first things to check on the NAS: whether its model measures alignment from the two files, copies text exactly, and keeps the title as the media search returns it. See `FINALIST_DAY.md`.
