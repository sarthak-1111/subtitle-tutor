# Install, setup, removal and a quick test

Linked from [SKILL.md](../SKILL.md).

## Requirements

- A UGREEN AI NAS running UGOS with the NAS assistant and Skills support. The finalist test device is the iDX6011 Pro.
- Films or series indexed in the NAS video library.
- Subtitle files in `.srt`, `.ass` or `.ssa` format next to the video files. Alternatively, the NAS video service's online subtitle search, used only after the user confirms.
- The NAS assistant allowed to use the video library, File Manager, document translation and text saving for the user's own files.

No account, API key, password or external service has to be configured for this Skill.

## Install

Install `subtitle-tutor` from UGREEN SkillHub, or import the Skill package (`subtitle-tutor` folder with `SKILL.md` and `references/`) through the Skill installation method UGREEN provides for the NAS assistant. The package contains Markdown files only: no scripts, binaries or settings.

## Setup

Nothing else is needed. The Skill creates `Language Lessons/<title>/` in the personal folder only when the first sheet is saved, and only after the user confirms. It starts no background job, schedule or service.

## Removal

1. Remove `subtitle-tutor` from the NAS assistant's Skill list. Nothing keeps running afterwards.
2. Study sheets, flashcard files and `studied: …` tags are ordinary user files and tags. They stay until the user deletes them in File Manager. Removing the Skill never deletes them.

## Quick test (about 10 minutes)

Use a film you own that has an English and a Spanish `.srt` file next to it in the same folder.

| # | Say | Expected result |
|---|---|---|
| 1 | "Make an intermediate Spanish lesson from [film title]. My language is English." | The title is found, both subtitle files are found, and the alignment check reports "aligned". A preview of 3 phrases is shown, and the save waits for your yes. After "yes", the reply gives the verified path in `Language Lessons/[film title]/`. |
| 2 | The same request again. | The earlier sheet is found. The new sheet has no repeated phrases and up to 3 review questions marked "(review)", and its file name does not replace the first one. |
| 3 | "Make a French lesson from a film I don't have." | "I could not find a title matching … in the NAS media library." The Skill stops. Nothing is downloaded or written. |

If case 1 reports "misaligned", the two subtitle files come from different releases. The Skill then offers translation instead of pairing the wrong lines, which is the intended behaviour.
