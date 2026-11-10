# Finalist day runbook: Subtitle Tutor

Use this only if we are selected. Finalist invitations go out on **Nov 21, 2026, 00:00 PT (17:00 JST)**. The assigned testing day falls between Nov 22 and Nov 28, and covers **00:00–23:59 PT, which is 17:00 JST on that date to 16:59 JST the next day**. Final package and video are due **Nov 30, 23:45 PT (Dec 1, 16:45 JST)**.

Ground rules from the Official Rules:

- Credentials go to the Representative only and are valid for the assigned day only.
- Use the NAS only to install, test and record this Skill.
- Back up logs and test data before the day ends; the NAS is reset afterwards.
- The demo video:
  - must be under 3 minutes;
  - must have English narration or complete English subtitles;
  - must be public on YouTube;
  - must show the Skill running on the assigned NAS;
  - must contain no third-party copyrighted music or material without permission.

---

## 1. Before the day (prepare on your PC after the invitation)

### 1.1 Test media

| Set | Title | Why | Files to put in its own folder |
|---|---|---|---|
| A | *His Girl Friday* (1940), about 92 min | US public domain (copyright not renewed; the underlying play *The Front Page* entered the US public domain in 2024). Dense everyday dialogue. Copy: archive.org item `HisGirlFriday-1940`. | `His Girl Friday (1940).mp4`, `His Girl Friday (1940).en.srt`, `His Girl Friday (1940).es.srt` |
| A-edge | Same film | Misalignment test fixtures | `His Girl Friday (1940).es-alt.srt` (drift version, see 1.2); keep `...es-shift.srt` (constant +4.0 s) in a separate fixtures folder |
| B | *Charade* (1963) | Widely listed as US public domain (released without a valid copyright notice). Used for the download test. | `Charade (1963).mp4` and `Charade (1963).en.srt` only, with **no Spanish file** |
| Fallback | *Tears of Steel* (2012, Blender Foundation, CC BY 3.0, 12 min) | Use if a set above cannot be prepared. Official `.srt` files in 8 languages (en, es, fr, de, nl, it, ru, no) at mango.blender.org/download. | Check the subtitle files' licence; credit "(CC) Blender Foundation, mango.blender.org" in the video. |

Checks before upload:

- **Public-domain status.** The status above is for the US. Check it for your country of residence, and keep a note of the source page for each film.
- **Subtitle files.** Record where each `.srt` came from, and its licence, in a short media log.
  - Prefer files whose licence allows reuse.
  - In the demo, show only short excerpts, which is how the Skill works anyway.
- **Timing.** Spot-check that `en.srt` and `es.srt` match your copy of set A. Open the film at three points (about 0:10, 0:45 and 1:20) and confirm the lines appear on cue. Core case 1 needs an aligned pair.
- **Encoding.** All `.srt` files must be UTF-8. Re-save them as UTF-8 if any text looks wrong.

### 1.2 Edge-case fixtures (made on your PC with any subtitle editor)

- `His Girl Friday (1940).es-shift.srt`: the aligned Spanish file with every timing moved +4.0 seconds. Expected result: "constant offset, corrected by 4.0 s".
- `His Girl Friday (1940).es-alt.srt`: the aligned Spanish file converted from 23.976 to 25 fps, which creates drift. Expected result: "misaligned".

### 1.3 Tools and files to have ready

- `dist/subtitle-tutor.zip`, built from the committed version, and `CHECK_RESULT.md`.
- The kit (`uliya-skill-kit` 0.7.3), installed in your AI assistant, so fixes can be re-checked during the day. Do not upload the kit to the NAS.
- Screen recorder (for example OBS) set to 1080p. A headset mic. Narration script (section 5) printed or on a second screen.
- A run log: one table row per run, with time, trigger sentence, delegations and states, approvals, output path and issues.

---

## 2. Timeline for the testing day (PT, with JST in brackets)

| Time (PT) | (JST) | Block | Done when |
|---|---|---|---|
| 00:00–01:00 | 17:00–18:00 | Connect with the emailed instructions. Change nothing on the NAS outside our test folders. Upload media sets A and B to a folder inside the video library. Let the video app finish indexing. | Both titles are visible in the NAS video app. |
| 01:00–02:00 | 18:00–19:00 | Install `subtitle-tutor` as described in UGREEN's finalist instructions. Confirm the NAS assistant lists it. | The Skill shows as installed. |
| 02:00–03:30 | 19:00–20:30 | Capability probes (section 3), by asking the NAS assistant directly. | Each probe has an answer in the run log. |
| 03:30–07:00 | 20:30–00:00 | Run core 1, core 2, the edge cases and repeat use (section 4). Fix the Skill where real behaviour differs, re-check with the kit, re-install, re-run. | All cases pass, or the gap is written up honestly. |
| 07:00–09:00 | 00:00–02:00 | Full rehearsal of the demo flow, start to finish, timed. | A run under 3 minutes without retries. |
| 09:00–12:00 | 02:00–05:00 | Rest. | |
| 12:00–15:00 | 05:00–08:00 | Record the demo footage, in 2 or 3 clean takes of each segment (section 5). | Every shot in the list is captured. |
| 15:00–19:00 | 08:00–12:00 | Edit the video, record the narration, add English subtitles. Upload to YouTube as public. | The video is live; the link opens while logged out. |
| 19:00–22:00 | 12:00–15:00 | Back up the saved sheets, run log, screenshots and the final Skill files. Rebuild the ZIP and re-check it. Spare time for re-shoots. | Backups are on the PC; the final ZIP is static-pass. |
| 22:00–23:59 | 15:00–16:59 | Buffer. Optionally remove our test folders. Log out. | |

---

## 3. Capability probes (from GO_NO_GO.md)

| # | Question | How to probe | If it differs |
|---|---|---|---|
| P1 | Does `ug-video` `search` return the file path? | Ask the assistant to search the video library for "His Girl Friday" and show the full result. | If there is no path, step 2 asks the user for the folder. Confirm that this fallback works. |
| P2 | Where does `subtitle-download` save, and how does language matching work? | Covered by core case 2, which lists the folder before and after. | Note the real location and file name pattern. If the file is saved elsewhere, update step 3 to use the reported path. |
| P3 | Does `ug-filesystem` `cat` return a 100 KB `.srt` in full? | Covered by core case 1. Compare the last cue time with the film length. | Adjust the chunk size in step 4. |
| P4 | Which translation pairs does `ug-document` `translate` support with inline content, and does it write an `output_file`? | Use T6, which needs en→ja. Also try en→es. | Record the supported pairs in the README and the Skill limits. |
| P5 | How does `ug-knowledge` `save-text` behave when a file of the same name exists? | Repeat-use run R1. | Keep the "new name by default" rule, and document the real behaviour. |
| P6 | How does approval behave for `ug-filemgr` `tag-add-file`, and is a colon allowed in a tag name? | Tag step in core case 1. | If the colon is rejected, the Skill already offers `studied-es-intermediate`. |
| P7 | Does `ug-video` `search` with play start playback, and where? | Replay step in core case 1. | If it does not, the Skill gives the timestamp only, as designed. |
| P8 | Does `ug-video` `search` with type `recent` list recently **played** titles (not recently added ones)? | Trigger T5 after playing set A for a minute. | If it lists recently added titles, change the step 2 wording to "recently added" or drop that entry point. |

---

## 4. Test cases: exact trigger sentences and expected results

Type each trigger sentence exactly as written. Write down every confirmation the Skill asks for, and every NAS approval prompt.

### Core case 1: both subtitle files present, full flow (media set A)

Triggers, in order:

1. **T1:** "Make an intermediate Spanish lesson from His Girl Friday. My language is English."
2. When asked to save: "Yes with flashcards."
3. **T1b**, after the save: "Replay phrase 3."
4. **T1c**, when asked to tag: "Yes, tag it."

| Step | Expected result |
|---|---|
| 1 Inputs | One-line summary: Spanish, intermediate, 20 phrases, whole film, translations into English. |
| 2 Title | One match, *His Girl Friday* (1940), movie, with its real path. No question asked. |
| 3 Subtitles | `.en.srt` and `.es.srt` found, with the language read from the file name. No download offered. If `es-alt.srt` is already in the folder, the Skill asks which Spanish file to use; choose `.es.srt`. |
| 4 Read | The lesson folder is listed first: it does not exist yet, and no earlier sheet is found. Then both files are read in full; the last cue is near the end of the film. |
| 5 Phrases | 20 phrases, at most 12 words each, spread over the film; the "Phrases per fifth" row matches the timestamps. No names, fillers, `[sound]` labels or credits. Spot-check five phrases word by word against the `.es.srt` file. |
| 6 Pairing | Alignment line with numbers, for example "10 of 10 anchors matched, median +0.0 s: aligned", and the anchor table: 10 rows, one from each tenth of the film, both lines quoted. Check three rows against the `.en.srt` file: each English time must be the start time of that English line (the stand-in model often copied the Spanish time instead). Every phrase has a translation marked "subtitle line". No translation call is made. |
| 7 Save | Preview with the full phrase list (number, time, phrase, translation) and the path `…/Language Lessons/His Girl Friday/His Girl Friday - Spanish intermediate - <date>.md`, using the title exactly as the media search returned it, with "folder will be created". Answer "yes with flashcards". NAS approval appears for the folder and each save. Result: verified, with the real path and byte count; the saved sheet contains the full text (open it), and the flashcard file has one tab-separated line per phrase. |
| 8 Replay | Phrase 3's timestamp minus 2 s, with the lines before and after. Offer to start the film. Seeking the player to that time shows the line on screen. |
| 9 Tag | Asks before tagging. NAS approval appears. The tag `studied: Spanish intermediate` is attached, and is visible in File Manager. |
| End | Final report: files used, 20 phrases (20 subtitle, 0 machine), aligned, saved path, tag added. |

### Core case 2: missing subtitle file downloaded after confirmation (media set B)

**T2:** "Make a beginner Spanish lesson from Charade with 10 phrases from the first 30 minutes. I speak English."

| Step | Expected result |
|---|---|
| 3 Subtitles | English found, Spanish missing. The Skill asks to search online and states that this contacts a subtitle source outside the NAS. Answer "yes". |
| 3 Search | Up to 5 Spanish candidates, with those matching the release name first. Pick the first one and confirm. |
| 3 Download | The NAS approval prompt appears; approve it. The folder is listed again, and exactly one new Spanish file is reported, with its real path. |
| 4–6 | Only cues from 00:00:00 to 00:30:00 are used. Alignment is aligned, offset-corrected, or misaligned; any of these is acceptable if reported with numbers. |
| 7 | 10 phrases saved after confirmation. |

### Edge case E1: misaligned subtitle versions (media set A plus `es-alt.srt`)

**T3:** "Make an advanced Spanish lesson from His Girl Friday, 15 phrases. My language is English."

Expected results:

1. Two Spanish files are found, and the Skill asks which one to use. Choose `es-alt.srt`.
2. Alignment: "misaligned", with the measured spread or cue-count gap shown. No timestamp pairing.
3. The Skill offers three choices: translation, another file, or stop. Choose translation. NAS approval appears.
4. The phrases are marked "machine translation". **Pass condition:** no phrase is paired with a wrong subtitle line.

### Edge case E2: constant offset

Repeat E1 with `es-shift.srt` in place of `es-alt.srt`.

Expected result: "offset of +4.0 s corrected". Pairing then goes ahead, marked "subtitle line".

### Edge case E3: title not found

**T4:** "Make a French lesson from Casablanca."

Expected result: "I could not find a title matching Casablanca in the NAS media library." The Skill stops. It does not suggest other titles and does not call any other expert.

### Edge case E4: unsupported or untested language pair (probe P4)

**T6:** "Make a beginner English lesson from His Girl Friday. My language is Japanese."

Expected results:

1. Japanese subtitles are missing, so the Skill offers an online search. Answer "no", to force the translation path.
2. The Skill translates with `document-agent`.
3. If `ja` is not supported, the Skill says so. It offers to save without translations (marked) or to stop, and never invents a translation.

### Repeat use R1

Run **T1** again on the same day.

Expected results:

- The same lesson folder as in T1 is listed (in one stand-in run the model added the year to the title, looked in the wrong folder and missed the earlier sheet).
- The earlier sheet is found and named in the preview.
- No phrase from the first sheet is repeated.
- 1 to 3 quiz questions are marked "(review)" and use phrases from the first sheet; the "Review" row names it.
- The new file gets a ` (2)` name. Nothing is overwritten.

### Recently watched R2

Play set A for a minute, then say **T5:** "Make a Spanish lesson from the film I watched last night."

Expected result: a list of recently watched titles with *His Girl Friday* in it, and a question asking which one to use (probe P8).

### Regression check with the test bench

Before the day, run `testbed/` with the final Skill (see `testbed/README.md`). On the day, compare each NAS run with the stand-in transcript of the same scenario, and note every difference in the run log.

Check first where the stand-in was weakest (`testbed/DEVLOG.md`, batch 3): whether the anchor table's English times come from the English file, whether phrases, context lines and subtitle translations are copied exactly, and whether the lesson folder uses the title as the media search returned it.

---

## 5. Demo video (under 3 minutes, English narration plus English subtitles)

Record at 1080p. Show the NAS UI and the assistant conversation. Use no background music. Film audio stays low, and only short clips are used.

| Time | Shot | Narration (outline) |
|---|---|---|
| 0:00–0:15 | NAS video library showing *His Girl Friday* | "My NAS holds films I have watched once. Subtitle Tutor turns them into language lessons, using the NAS's own capabilities." |
| 0:15–0:25 | File Manager: film folder with `.en.srt` and `.es.srt` | "Here is a public-domain film with English and Spanish subtitles beside it." |
| 0:25–1:15 | Type T1. Title found, subtitles found, alignment "aligned", preview, save confirmation, NAS approval, verified path | "One sentence. It finds the title and both subtitle files, checks that their timings line up, picks 20 phrases for my level, and asks before it saves anything." |
| 1:15–1:40 | Open the saved sheet: phrases, timestamps, context, usage notes, quiz | "Each phrase has its translation from the real subtitle line, the exact timestamp, the lines around it, and a short usage note. A 10-question quiz is at the end." |
| 1:40–1:58 | "Replay phrase 3", then the player at that time shows the line | "Every phrase points back to its scene. The Skill gives the exact time to jump to." |
| 1:58–2:20 | E1: misaligned file, the Skill reports numbers and offers translation | "If the subtitles come from different versions, it measures the mismatch and says so, instead of pairing the wrong lines." |
| 2:20–2:40 | T2 download: confirmation text "outside the NAS", NAS approval, new file found | "A missing subtitle file is downloaded only after I confirm. That is the only time anything leaves the NAS." |
| 2:40–2:55 | Tag `studied: Spanish intermediate` in File Manager | "With my OK it tags the film, so next time I get new phrases." |
| 2:55–3:00 | End card: Subtitle Tutor, UGREEN Hackathon 2026 | |

Recording checklist:

- Capture the exact confirmation messages and every NAS approval prompt. They demonstrate Technical Quality.
- Capture the verified save result, with path and byte count. It proves a real result.
- Do not show credentials, the connection URL, or any personal data.

YouTube upload:

- **Title:** "Subtitle Tutor: language lessons from your NAS films (UGREEN Hackathon 2026)".
- **Visibility:** public.
- **Captions:** English.
- **Description:**
  - one paragraph on what it does;
  - the capability chain;
  - "Film: His Girl Friday (1940), public domain in the US";
  - the AI tools disclosure.

---

## 6. Before the session ends (backup) and after the day

1. Save each generated study sheet. Download them, or copy the text from the conversation.
2. Save the run log, the screenshots of every confirmation and approval, and any expert error messages.
3. If the Skill was changed during the day:
   - re-run the kit check until it is static-pass;
   - update `CHECK_RESULT.md`;
   - rebuild `dist/subtitle-tutor.zip`;
   - commit the change.
4. Update the honesty statements. Replace "not yet run on a NAS" with what was actually observed, including anything that did not work.
5. Submit through the private Round 2 link by **Nov 30, 23:45 PT**:
   - the final ZIP;
   - the YouTube link.
6. Do not delete the Round 1 materials.
