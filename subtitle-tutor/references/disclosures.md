# Disclosures

This page is linked from [SKILL.md](../SKILL.md). It gives the disclosures required for the UGREEN Hackathon 2026 on AI NAS.

## Third-party components and licences

**None in the Skill package.**

- The Skill consists of six Markdown files written for this entry: `SKILL.md` and five files in `references/`.
- It contains no third-party code, libraries, models, datasets, images, fonts or text.
- It contains no scripts, executables or binaries.
- [example-sheet.md](example-sheet.md) quotes only "Quay Three", a short French and English test script written for this entry and released as CC0. No line from a real film is used anywhere.

The Skill relies only on NAS capabilities provided by UGOS through its registered experts:

- `media-agent`
- `file-agent`
- `document-agent`
- `knowledge-agent`

These are part of the NAS platform. They are not bundled with or redistributed by this Skill.

### Test tools outside the package

The public repository also has an off-device test bench in `testbed/`. It is not part of the Skill package and is not installed on the NAS.

| Component | Licence | Use |
|---|---|---|
| Test scripts in `testbed/` (Python standard library only) | MIT, written for this entry | Build the test subtitles, emulate the NAS experts, the approval prompt and the user, and score each run. |
| "Umbrella Weather" test subtitles | CC0, written for this entry | Spanish and English test files, including shifted, drifting, noisy and `.ass` variants. |
| Ollama | MIT | Serves the stand-in model on a PC. |
| gpt-oss-120b (OpenAI, open weights) | Apache-2.0 | Plays the NAS assistant in the stand-in runs. |

## External services and data flows

The only connection the Skill makes outside the NAS is the optional online subtitle search and download in step 3.

- **How it runs:** it is performed by the NAS video service (`ug-video` `subtitle-search` and `subtitle-download`) and runs only after the user's explicit yes. The NAS may also ask for its own approval.
- **Which source:** the online subtitle source used by the NAS video service is not named in the public capability catalog.
- **What is sent:** the film's details needed for the search.
- **What comes back:** one subtitle file, saved by the NAS.

No other data leaves the NAS because of the Skill. It has no sharing, upload or messaging step. Reasoning runs on the model the NAS assistant uses, under the assistant's own settings.

## Licence of this Skill

MIT License. Copyright (c) 2026 sarthak-1111.

## Principal functionality developed for this Hackathon

Everything in this package was designed and written during the Hackathon period, in November 2026. None of it was taken from an earlier Skill. UGREEN's own SkillHub Skill "Smart subtitle matching" already finds and downloads subtitles; Subtitle Tutor starts where that ends and turns the subtitles into a lesson. It covers:

- The end-to-end orchestration from a title, or from something recently watched, to a saved study sheet:
  - title lookup with a choice when there are several matches, and series episodes;
  - local subtitle discovery with language detection;
  - confirmed online subtitle download, with a before and after check of the video folder;
  - chunked reading of the subtitle text, with an encoding check and block-wise work on long files;
  - a confirmed save without silent overwrite, and an optional flashcard file;
  - an optional replay timestamp and an optional "studied" tag.
- Phrase selection rules by level, usefulness, frequency and spread, with filters for names, fillers, sound descriptions, lyrics, signs, credits and adverts.
- The subtitle alignment check: 10 anchors matched by meaning, a table shown to the user, and one of three results (aligned, constant offset, misaligned).
- The study sheet format, with context lines, usage notes, a 10-question self-quiz and an answer key.
- Repeat use: the newest earlier sheet for the title is read, its phrases are not chosen again, and up to 3 quiz questions review them.
- The failure handling for every delegation state and every failure listed in SKILL.md.

## AI tools used and their principal uses

| Tool | Used for |
|---|---|
| Claude Code (Anthropic), model Claude Opus 5.5 | Reading the Hackathon rules and the creation-tool documentation; drafting and revising the Skill text, the test bench and the submission documents; running the official static check and fixing what it reported. The entrant chose the idea, directed the work and reviewed the result. |
| UGOS Skill Creation Tool `uliya-skill-kit` 0.7.3 (UGREEN) | Capability catalog for the feasibility check, generation guidance, and the official static check. The tool is not included in this package. |
| gpt-oss-120b via Ollama | Off-device stand-in for the NAS assistant in `testbed/`. Not used for any file in this package. |

## Models at run time

The Skill adds no AI service of its own. Phrase choice, usage notes and the quiz are produced by the model the NAS assistant is configured to use. Translation is done by `document-agent`.

## Version history

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-11-09 | First version: title lookup, subtitle discovery and confirmed download, phrase selection, alignment check, study sheet with quiz, confirmed save, replay timestamp, "studied" tag. |
| 1.1.0 | 2026-11-09 | Start from recently watched titles; series episode naming; review of the latest earlier sheet; optional flashcard file; anchor table for the alignment check; encoding check; block-wise work on long subtitle files; example sheet; install and test guide; off-device test bench in the repository. |
