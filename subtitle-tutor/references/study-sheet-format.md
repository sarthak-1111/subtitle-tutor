# Study sheet and flashcard format

Read this file in step 7 of [SKILL.md](../SKILL.md). The sheet is one Markdown file. All explanations are written in the user language; phrases stay in the target language exactly as they appear in the subtitles. [example-sheet.md](example-sheet.md) shows a finished sheet.

## File names

- **Sheet:** `{TITLE_SAFE} - {TARGET_LANG} {LEVEL} - YYYY-MM-DD.md`, with today's date. For a series, put the episode after the title: `{TITLE_SAFE} {EP_TAG} - {TARGET_LANG} {LEVEL} - YYYY-MM-DD.md`. Examples: `Charade - Spanish intermediate - 2026-11-22.md`, `Night Shift S01E03 - Japanese beginner - 2026-11-22.md`.
- **Flashcards:** the sheet name with ` - flashcards.txt` in place of `.md`.
- If a name already exists in the destination folder, add ` (2)`, ` (3)` and so on before the extension.

## Sheet layout

The layout below is a format specification. Words in curly braces are filled at run time from the real results of steps 2 to 6.

```markdown
# {TITLE} {EP_TAG}: {TARGET_LANG} phrases ({LEVEL})

For personal study. Short excerpts from the subtitles of a title in your own NAS library.

| | |
|---|---|
| Made on | {DATE} with Subtitle Tutor |
| Target-language subtitles | {TARGET_SUB file name} |
| Translations from | {TRANSLATION_SOURCE} |
| Scene range | {SCENE_RANGE} |
| Alignment | {ALIGNMENT} |
| Phrases | {real number} of {requested number} |
| Phrases per fifth | {COVERAGE} |
| Review | {REVIEW} |

## Phrases

### 1. {phrase}
- **When:** {HH:MM:SS}
- **Meaning:** {translation} *({SOURCE})*
- **Before:** {line before}
- **After:** {line after}
- **Usage:** {usage note}

(one block per phrase, numbered in timestamp order)

## Self-quiz

1. Say it: "{meaning, in the user language}"
2. Fill the gap: "{the target-language phrase, with one key word replaced by ____}"
3. What does it mean: "{the target-language phrase}" a) {meaning} b) {meaning} c) {meaning}
4. Which situation: {everyday situation, in the user language}. Which phrase from this sheet fits?
...
10. {question}

## Answers

1. {answer} (phrase {number}, {HH:MM:SS})
...
10. {answer} (phrase {number}, {HH:MM:SS})

## Notes

- {flags: partial read, encoding problem, fewer phrases than requested, misaligned versions, untranslated phrases}
- Usage notes and quiz questions were written by the assistant from the subtitle text. Check nuance with a teacher or a native speaker.
```

Fill each field with exactly one of these:

| Field | Value |
|---|---|
| `{TRANSLATION_SOURCE}` | The user-language subtitle file name; or `NAS machine translation`; or, when both were used, the file name followed by `and NAS machine translation`. |
| `{SCENE_RANGE}` | `whole title`, or `{START} to {END}`. |
| `{ALIGNMENT}` | `aligned`; `offset of {N} s corrected`; or `not used: {reason}`, for example `not used: misaligned (drift)` or `not used: no user-language subtitles`. |
| `{COVERAGE}` | Five numbers separated by ` / `: how many phrases come from each fifth of the scene range, counted from the phrase times, for example `4 / 4 / 4 / 4 / 4`. |
| `{REVIEW}` | The file name of the earlier sheet used for review, or `none`. |
| `{SOURCE}` | `subtitle line`, `machine translation` or `no translation available`. A phrase without a translation is written `- **Meaning:** — *(no translation available)*`. |

## Usage notes

Each usage note is at most 25 words in the user language. It says when to use the phrase (the situation and the register: polite, neutral or informal) and one point of grammar or nuance. At advanced level it adds a register warning for informal or rude language. Notes never retell the plot.

## Self-quiz

The quiz always has 10 questions, built only from phrases on this sheet and, for review, from the earlier sheet:

| Count | Question type | The question shows | The answer is |
|---|---|---|---|
| 4 | **Say it** | The meaning in the user language. | The target-language phrase. |
| 3 | **Fill the gap** | The target-language phrase with one key word replaced by `____`. | The missing target-language word. |
| 2 | **What does it mean** | The target-language phrase and three meanings a), b), c) in the user language: one correct, two plausible but clearly different. | The letter and the correct meaning. |
| 1 | **Which situation** | An everyday situation described in the user language. | The target-language phrase from the sheet that fits it. |

- **Review:** when an earlier sheet was read in step 4, up to 3 of the "Say it" and "Fill the gap" questions use phrases from it instead. Mark them "(review)" and, in the answers, give that sheet's date and the phrase's timestamp.
- If the sheet has fewer than 5 phrases, use each phrase for more than one question type so there are still 10 questions.
- A question never shows its own answer: no arrows, hints, "(answer: …)" notes or solutions after it. "What does it mean" questions list their three options a), b) and c) on the same line.
- "Fill the gap" and "What does it mean" quote the target-language phrase from the sheet, never its translation. The gap in "Fill the gap" replaces a target-language word.
- Every answer, multiple-choice answers included, ends with the phrase number and timestamp in brackets, for example `(phrase 4, 00:14:18)`, so the learner can replay the scene. A review answer ends with the earlier sheet's date and the timestamp instead.
- Answers come after all questions, under their own heading.

## Flashcard file

Plain text, one card per line, three fields separated by a single tab character, no header line:

```text
{phrase}	{translation}	{TITLE} {EP_TAG} {HH:MM:SS}
```

Use only phrases that have a translation; leave out phrases marked "no translation available". Most flashcard apps import this as "text separated by tabs".

## Excerpt limits

| Item | Limit |
|---|---|
| Phrase | at most 12 words |
| Context line | at most 15 words |
| Quoted text per phrase block | at most three lines |

The sheet never contains the full subtitle file and never contains whole scenes.
