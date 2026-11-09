# Subtitle Tutor: Round 1 Proposal

UGREEN Hackathon 2026 · Open Innovation · sarthak-1111

## 1. What does the Skill do?

Subtitle Tutor turns a film or series already on your NAS into a language lesson. Each phrase, chosen for your level, gets a translation and its exact timestamp, plus a self-quiz.

## 2. Target user and problem

Language learners, expats, and parents preparing family lessons. Subtitled films teach well, but useful phrases scroll past, and making flashcards means pausing, copying and translating line by line.

## 3. Solution

"Make an intermediate Spanish lesson from Charade" produces a study sheet in Language Lessons/<title>/. Phrases are chosen by level, usefulness and frequency, and each links to its scene.

## 4. Core user flow

Request → title confirmed → subtitles found in both languages (missing ones downloaded after confirmation) → timestamped text read → phrases selected and translated → preview → saved after confirmation → optional replay timestamp or "studied" tag.

## 5. Difference from existing tools

Chat AI tools need uploaded subtitles and lose timings. Subtitle Tutor works in place on your own library and ties each phrase to its scene. It prefers human subtitle translations, measures alignment instead of guessing, and tracks progress through tags and earlier sheets.

## 6. NAS capabilities by step

- **Find title:** ug-video search
- **Find subtitles:** ug-filesystem ls
- **Download:** ug-video subtitle-search, subtitle-download
- **Read:** ug-filesystem cat
- **Translate gaps:** ug-document translate
- **Save:** file-workflow get-user-dir, ug-filesystem mkdir, ug-knowledge save-text
- **Tag:** ug-filemgr tag-add-file

## 7. Technical approach

Markdown-only orchestration. Each NAS operation is delegated to media-, file-, document- or knowledge-agent with a self-contained instruction that uses only real earlier results. All five delegation states are handled.

- **Inputs:** title, both languages, level, phrase count, optional scene range.
- **Permissions:** every write needs user confirmation plus NAS approval. Nothing is deleted, moved or shared.
- **Model:** reasoning uses the NAS assistant's model, intended to be local.
- **Outside connection:** only the confirmed subtitle download.

## 8. Development status

- **Built:** SKILL.md plus three references. Official checker: static-pass, 0 errors, 0 warnings.
- **Not built:** nothing further before NAS testing.
- **Pending NAS validation:** all runtime behaviour. Nothing has run on a NAS yet.

## 9. Validation plan

- **Core 1:** a public-domain film with English and Spanish .srt files → a saved 20-phrase sheet, with timestamps spot-checked.
- **Core 2:** Spanish subtitles missing → download after confirmation, then the sheet is built.
- **Edge:** subtitles from another release → misalignment reported, translation offered, no wrong pairings.

## 10. Limits, risks, dependencies

- The catalog has no video seek; replay gives the timestamp.
- Translation pairs and the download location are undocumented. Both are checked and reported at runtime.
- Embedded subtitle tracks are not read.
- Downloads depend on the NAS's online subtitle source.
- Long files may strain a local model. Scene ranges help.

---

Third-party components: none. Licence: MIT. AI tools: Claude Code (drafting, checking); UGOS Skill Creation Tool 0.7.3 (capability and static checks; not included).
