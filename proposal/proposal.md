# Subtitle Tutor: Round 1 Proposal

UGREEN Hackathon 2026 · Explore Your Imagination (Open Innovation) · sarthak-1111

## 1. What does the Skill do?

It turns a film or series already on your NAS into a language lesson: phrases chosen for your level, each with a translation, timestamp, surrounding lines and a usage note, plus a 10-question quiz.

## 2. Target user and problem

People learning a language with subtitled films. Useful phrases pass in seconds, and collecting them means pausing, copying and translating line by line.

## 3. Solution

Say "Make an intermediate Spanish lesson from Charade". The assistant reads both subtitle files, picks phrases from across the whole film, pairs each with the subtitle line spoken at the same moment, and saves a sheet, plus optional flashcards, in Language Lessons/<title>/. The next lesson skips known phrases and reviews three.

## 4. Core user flow

Request, or "the film I watched last night" → title found → subtitles found (a missing file downloaded only after a yes) → text read → alignment measured → phrases chosen → preview → saved after a yes → optional tag and replay timestamp.

## 5. Difference from existing tools

UGREEN's Smart subtitle matching finds subtitle files; Subtitle Tutor turns them into lessons. Chat tools need uploads and lose timings. This works in place, prefers human subtitle translations, measures alignment instead of assuming it, and remembers earlier lessons.

## 6. NAS capabilities by step

- **Find title, recently watched:** ug-video search
- **Find, read subtitles:** ug-filesystem ls, cat
- **Download (after a yes):** ug-video subtitle-search, subtitle-download
- **Translate gaps:** ug-document translate
- **Save:** file-workflow get-user-dir, ug-filesystem mkdir, ug-knowledge save-text
- **Tag:** ug-filemgr tag-add-file

## 7. Technical approach

Markdown only: SKILL.md and five references. Every NAS action is delegated to media-, file-, document- or knowledge-agent using only real earlier results; all five delegation states are handled. Writes need the user's yes plus NAS approval. Nothing is deleted, moved or shared; the only outside connection is the confirmed download.

## 8. Development status

- **Built:** the Skill (official checker: static-pass, 0 warnings) and a test bench with original subtitles, emulated experts and a scripted user.
- **Stand-in tests (PC, not the NAS):** gpt-oss-120b follows SKILL.md in 10 scenarios, including offset, drift, download and a repeat lesson. Final round: 310 of 360 automatic checks passed; workflow and safety 131 of 135, alignment only 19 of 32.
- **Pending:** all on-device behaviour.

## 9. Validation plan

On the finalist device, with a public-domain film:

- English and Spanish .srt → 20-phrase sheet; timestamps checked during playback.
- Spanish file missing → confirmed download, then sheet.
- Subtitles from another release → misalignment reported, no wrong pairs.

## 10. Limits, risks, dependencies

- No video seek in the catalog: replay gives the timestamp.
- Translation pairs and the download location are undocumented; both are checked at run time.
- Embedded subtitle tracks are not read.
- The stand-in measured alignment poorly (but never paired wrongly); a smaller NAS model may do worse.

---

Third-party components: none in the package; the test bench uses Ollama (MIT) and gpt-oss-120b (Apache-2.0). Licence: MIT. AI tools: Claude Code (drafting, test bench); UGOS Skill Creation Tool 0.7.3 (catalog, static check; not included).
