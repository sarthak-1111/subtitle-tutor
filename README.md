# Subtitle Tutor

Subtitle Tutor is a UGOS Skill for UGREEN AI NAS. It turns films and series you already own on the NAS into language lessons:

- it finds the subtitles;
- it picks useful phrases for your level;
- it pairs each phrase with a translation and its exact timestamp;
- after you confirm, it saves a study sheet with a self-quiz next to your notes.

This is an entry for the [UGREEN Hackathon 2026 on AI NAS](https://ugreenhackathon.devpost.com) (Round 1, Open Innovation track).

> **Status:** Round 1 pre-test package.
>
> The Skill passes the official UGOS Skill Creation Tool static check (`static-pass`, 0 errors, 0 warnings). **It has not yet run on a real UGREEN NAS.** Device validation is planned for the finalist testing day.

## Repository layout

| Path | What it is |
|---|---|
| [`subtitle-tutor/`](subtitle-tutor/) | **The Skill package.** It holds `SKILL.md` plus three linked references, and nothing else. |
| `dist/subtitle-tutor.zip` | The same folder as a ZIP, as submitted on Devpost. |
| [`proposal/`](proposal/) | The Round 1 proposal (`proposal.md` and `proposal.pdf`). It answers the ten official items in 409 words. |
| [`GO_NO_GO.md`](GO_NO_GO.md) | Feasibility check against the official capability catalog, with exact CLI and Action names. |
| [`COMPLIANCE.md`](COMPLIANCE.md) | Checklist of the hackathon rules, the starter kit, the SkillHub publishing standards and the checker rules. |
| [`CHECK_RESULT.md`](CHECK_RESULT.md) | Output of the official static check. |
| [`FINALIST_DAY.md`](FINALIST_DAY.md) | 24-hour runbook for the NAS testing day and the demo video. |
| [`devpost.md`](devpost.md) | Submission text, mapped to the judging criteria. |

## How the Skill works

| Step | Expert | Capability |
|---|---|---|
| Find the title | `media-agent` | `ug-video` `search` |
| Find subtitle files | `file-agent` | `ug-filesystem` `ls` |
| Download a missing subtitle (confirmed) | `media-agent` | `ug-video` `subtitle-search`, `subtitle-download` |
| Read the timestamped text | `file-agent` | `ug-filesystem` `cat` |
| Translate the gaps | `document-agent` | `ug-document` `translate` |
| Save the sheet (confirmed) | `knowledge-agent` | `ug-knowledge` `save-text` |
| Tag the video as studied (confirmed) | `file-agent` | `ug-filemgr` `tag-add-file` |

The full workflow, confirmations and failure handling are in [`subtitle-tutor/SKILL.md`](subtitle-tutor/SKILL.md).

## Not included

The official UGOS Skill Creation Tool (`uliya-skill-kit`) was used to build and check this Skill. It is **not** redistributed here. Download it from the [Hackathon Starter Kit](https://ai.ugreen.com/pages/hackathon-starter-kit).

## Disclosures

- **Third-party components:** none.
- **AI tools:** Claude Code (Anthropic), used for drafting and checking the text.

Details are in [`subtitle-tutor/references/disclosures.md`](subtitle-tutor/references/disclosures.md).

## License

[MIT](LICENSE) © 2026 sarthak-1111
