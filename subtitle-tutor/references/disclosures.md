# Disclosures

This page is linked from [SKILL.md](../SKILL.md). It gives the disclosures required for the UGREEN Hackathon 2026 on AI NAS.

## Third-party components and licences

**None.**

- The Skill consists of four Markdown files written for this entry: `SKILL.md` and three files in `references/`.
- It contains no third-party code, libraries, models, datasets, images, fonts or text.
- It contains no scripts, executables or binaries.

The Skill relies only on NAS capabilities provided by UGOS through its registered experts:

- `media-agent`
- `file-agent`
- `document-agent`
- `knowledge-agent`

These are part of the NAS platform. They are not bundled with or redistributed by this Skill.

## External services and data flows

The only connection outside the NAS is the optional online subtitle search and download in step 3.

- **How it runs:** it is performed by the NAS video service (`ug-video` `subtitle-search` and `subtitle-download`) and runs only after the user's explicit yes. The NAS may also ask for its own approval.
- **Which source:** the online subtitle source used by the NAS video service is not named in the public capability catalog.
- **What is sent:** the film's details needed for the search.
- **What comes back:** one subtitle file, saved by the NAS.

No other data leaves the NAS. The Skill has no sharing, upload or messaging step.

## Licence of this Skill

MIT License. Copyright (c) 2026 sarthak-1111.

## Principal functionality developed for this Hackathon

Everything in this package was designed and written during the Hackathon period, starting in November 2026. None of it was taken from an earlier Skill. It covers:

- The end-to-end orchestration from a title to a saved study sheet:
  - title lookup with a choice when there are several matches;
  - local subtitle discovery with language detection;
  - confirmed online subtitle download, with a before and after check of the video folder;
  - chunked reading of the subtitle text;
  - a confirmed save without silent overwrite;
  - an optional replay timestamp and an optional "studied" tag.
- Phrase selection rules by level, usefulness, frequency and spread, including the filters for names, fillers, sound descriptions, credits and adverts.
- The subtitle alignment check (aligned, constant offset, misaligned), with measured numbers reported to the user.
- The study sheet format, with context lines, usage notes, a 10-question self-quiz and an answer key.
- Repeat use: earlier sheets in the lesson folder are found, so new phrases can be chosen, and the "studied" tag shows progress.
- The failure handling for every delegation state and every failure listed in SKILL.md.

## AI tools used and their principal uses

| Tool | Used for |
|---|---|
| Claude Code (Anthropic), model Claude Opus 5.5 | Reading the Hackathon rules and the creation-tool documentation; drafting and revising the Skill text, the proposal and the checklists; running the official static check and fixing what it reported. The entrant defined the idea, approved the feasibility check and reviewed the result. |
| UGOS Skill Creation Tool `uliya-skill-kit` 0.7.3 (UGREEN) | Capability catalog for the feasibility check, generation guidance, and the official static check. The tool is not included in this package. |

## Models at run time

The Skill adds no AI service of its own. Phrase choice, usage notes and the quiz are produced by the model the NAS assistant is configured to use, which is meant to be the NAS's local model. Translation is done by `document-agent`.
