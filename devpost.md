# Devpost submission text: Subtitle Tutor

Paste each block into the matching Devpost field. The judging-criteria names below are the official ones from the Rules (§6): User Value, Innovation & Differentiation, Technical Quality, AI NAS Fit & Validation. They correspond to the brief's "Usefulness", "Creativity", "Technical Execution" and "AI NAS Fit".

---

## Project name

Subtitle Tutor

## Elevator pitch (at most 200 characters)

Turn the films and series already on your UGREEN NAS into language lessons: level-matched phrases with translations, exact timestamps and a self-quiz, saved next to your notes.

## Track

Open Innovation

## Built with (tags)

`markdown` · `ugos` · `uliya-skill-kit` · `ugreen-ai-nas` · `claude-code`

## Files to upload

- `proposal/proposal.pdf` (Project Proposal, 2 pages, 61 KB)
- `dist/subtitle-tutor.zip` (Pre-test Skill Package, 16 KB)

## Try it out (optional)

Leave this empty, or use the public repository link if it was created: https://github.com/sarthak-1111/subtitle-tutor

---

## About the project (paste into the main description; Markdown)

### Inspiration

Many people learn languages with subtitled films. The useful lines go by in a second, though, and turning them into study notes means pausing, copying and translating line by line. Meanwhile a NAS often holds hundreds of films and series that are only ever watched once. Subtitle Tutor turns that library from storage into something you study with.

### What it does

You name a title and the language you are learning. Optionally you add your level (beginner, intermediate or advanced), the number of phrases and a scene range. Subtitle Tutor then works in five stages:

1. **Find the title.** It finds the title in the NAS media library and asks you to choose if there are several matches.
2. **Find the subtitles.** It looks for subtitle files in both languages next to the video. If one is missing, it offers to download it, but only after telling you this fetches a file from outside the NAS.
3. **Read and choose.** It reads the subtitle text with timestamps and picks the most useful phrases for your level. Names, one-word fillers, sound labels, credits and adverts are excluded.
4. **Translate.** It pairs each phrase with a translation. It prefers the other-language subtitle at the same timestamp, and uses the NAS translation capability only for the gaps. Before relying on timestamps, it measures whether the two subtitle files are aligned.
5. **Save.** It writes a study sheet: each phrase with its translation, timestamp, the line before and after, and a usage note, followed by a 10-question self-quiz. The sheet is saved to `Language Lessons/<title>/` only after you confirm, and an existing file is never overwritten without asking.

On request it gives the exact timestamp to replay a phrase. After confirmation it can tag the video `studied: <language> <level>`, so your progress is visible later.

### How it works: capability chain

| Step | Expert | Catalog capability |
|---|---|---|
| Find title | `media-agent` | `ug-video` `search` |
| Find subtitle files | `file-agent` | `ug-filesystem` `ls`, `ug-filemgr` `tag-get-file` |
| Download missing subtitles (confirmed) | `media-agent` | `ug-video` `subtitle-search`, `subtitle-download` |
| Read timestamped text | `file-agent` | `ug-filesystem` `cat` (chunked) |
| Translate unmatched phrases | `document-agent` | `ug-document` `translate` |
| Save the sheet (confirmed) | `file-agent`, `knowledge-agent` | `file-workflow` `get-user-dir`, `ug-filesystem` `stat` / `mkdir`, `ug-knowledge` `save-text` |
| Replay | `media-agent` | `ug-video` `search` (play) plus the exact timestamp |
| Tag as studied (confirmed) | `file-agent` | `ug-filemgr` `tag-get-by-name`, `tag-add`, `tag-add-file` |

### How we built it

- The entrant defined the idea.
- Feasibility was checked against the official UGOS Skill Creation Tool (`uliya-skill-kit` 0.7.3) and its capability catalog, CLI by CLI, before any file was generated.
- The Skill was then generated with the same tool and checked with its official static checker. The result is **static-pass with 0 errors and 0 warnings**.
- The package is Markdown only: `SKILL.md` and three linked references (phrase selection and alignment, study-sheet format, disclosures).
- Claude Code (Anthropic) was used to draft and check the text. All disclosures are in `references/disclosures.md`.

### Challenges

The catalog leaves three gaps that the Skill handles honestly instead of guessing:

- **No video seek.** Replay gives the exact timestamp to jump to.
- **No published list of translation pairs.** Subtitle-to-subtitle pairing comes first. Machine translation covers only the gaps, and an unsupported pair is reported, never invented.
- **No documented save location for downloaded subtitles.** The Skill lists the video folder before and after the download and uses only a file it actually finds.

### Accomplishments

- **Real data only.** Every step passes on the real result of the previous one: paths, `file-id` values and text.
- **Explicit states.** All five delegation states (`completed`, `failed`, `cancelled`, `waiting_user`, `waiting_approval`) are handled explicitly.
- **Failures named.** The failure catalogue covers a missing title, missing subtitles, an unsupported language pair, misaligned subtitle versions, partial reads, a short phrase list and save conflicts.
- **Measured alignment.** The two subtitle files are compared by measurement (aligned, constant offset corrected, or misaligned), and the numbers are shown to the user.

### What we learned

Orchestration Skills are strongest when each expert does one verifiable thing and the Skill refuses to fill gaps with assumptions. Writing down "what if nothing is found" for every step shaped the design more than the happy path did.

### What's next (finalist testing day)

Nothing has run on a real UGREEN NAS yet. On the testing day we will validate the open runtime questions:

- the fields returned by the media search;
- the download location;
- which translation pairs work;
- save and overwrite behaviour;
- tag approval.

We will run two core cases and one edge case on a public-domain film, then fix anything that behaves differently, re-check and record the demo.

---

## How it meets the judging criteria (for your reference; paste only if a form field asks)

**User Value.** It solves a concrete problem: learning from films you already own without manual note-taking. The workflow is clear (one request, two or three confirmations) and gives useful feedback at each step: the matches found, the subtitles found or missing, the alignment result and a preview. The result is a saved study sheet with a quiz that you can use straight away.

**Innovation & Differentiation.** Most chat AI tools need the subtitle text uploaded and lose the timings. Subtitle Tutor works in place on the user's own library and keeps every phrase tied to its scene. It prefers human subtitle translations over machine translation and measures subtitle alignment rather than assuming it. It also remembers progress through NAS tags and earlier sheets, so a second run picks new phrases.

**Technical Quality.**

- Markdown-only Skill that passes the official static check with 0 errors and 0 warnings.
- Delegation only to registered experts, with self-contained instructions that carry real values.
- Explicit handling of all five delegation states and of every listed failure.
- Every write action needs user confirmation plus NAS approval: download, folder creation, save, overwrite and tag.
- No delete, move or share actions exist.
- No credentials and no scripts.
- Third-party components: none.

**AI NAS Fit & Validation.** The Skill only makes sense on a NAS: the media library, the subtitle files beside each video, the file tags and the lesson folder all live there. It chains media, file, document and knowledge capabilities. Reasoning runs on the NAS assistant's model, intended to be local, and nothing leaves the NAS except a subtitle download the user approved. Validation is planned for the finalist day, with two core cases and one edge case. No on-device results are claimed yet.

---

## Disclosures (if the form asks)

- **Third-party components and licences:** none. The package contains no third-party code, libraries, models, datasets or media. The Skill itself is under the MIT licence.
- **External services and data flows:** only the optional online subtitle search and download, run by the NAS video service after explicit user confirmation.
- **AI tools used:**
  - Claude Code (Anthropic, model Claude Opus 5.5) for reading the rules and tool documentation, drafting and revising the Skill and submission text, and running and acting on the official static check.
  - UGOS Skill Creation Tool `uliya-skill-kit` 0.7.3 for the capability catalog, generation guidance and the static check. The tool is not included in the package.
- **Development status:** the Skill package and proposal are complete for Round 1. No NAS runtime testing has been done yet.
