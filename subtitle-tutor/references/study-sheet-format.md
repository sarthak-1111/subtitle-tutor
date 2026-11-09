# Study sheet format

Read this file in step 7 of [SKILL.md](../SKILL.md). The sheet is one Markdown file. All explanations in it are written in the user language. Phrases stay in the target language, exactly as they appear in the subtitles.

## File name

The file name is `{TITLE_SAFE} - {TARGET_LANG} {LEVEL} - YYYY-MM-DD.md`, using today's date. Example: `Charade - Spanish intermediate - 2026-11-22.md`.

If that name already exists in the destination folder, add ` (2)`, ` (3)` and so on before `.md`.

## Layout

The layout below is a format specification. Words in curly braces are filled at run time from the real results of steps 2 to 6.

```markdown
# {TITLE}: {TARGET_LANG} phrases ({LEVEL})

For personal study. Short excerpts from the subtitles of a title in your own NAS library.

| | |
|---|---|
| Made on | {DATE} with Subtitle Tutor |
| Target-language subtitles | {TARGET_SUB file name} |
| Translations from | {USER_SUB file name} / NAS machine translation / mixed |
| Scene range | whole title / {START} to {END} |
| Alignment | aligned / offset of {N} s corrected / not used: {reason} |
| Phrases | {real number} of {requested number} |

## Phrases

### 1. {phrase}
- **When:** {HH:MM:SS}
- **Meaning:** {translation} *(subtitle line / machine translation / no translation available)*
- **Before:** {line before}
- **After:** {line after}
- **Usage:** {usage note}

(one block per phrase, numbered in timestamp order)

## Self-quiz

1. {question}
...
10. {question}

## Answers

1. {answer} (phrase {number}, {HH:MM:SS})
...
10. {answer} (phrase {number}, {HH:MM:SS})

## Notes

- {flags: partial read, fewer phrases than requested, misaligned versions, untranslated phrases}
- Usage notes and quiz questions were written by the assistant from the subtitle text. Check nuance with a teacher or a native speaker.
```

## Usage notes

Each usage note is at most 25 words in the user language. It covers:

- **When to use it:** the situation and the register (polite, neutral, informal);
- **one point of grammar or nuance;**
- **a register warning** for informal or rude language at advanced level.

Notes must not retell the plot.

## Self-quiz

The quiz always has 10 questions, built only from the phrases on this sheet:

| Count | Question type |
|---|---|
| 4 | **Say it:** give the meaning in the user language; the learner recalls the target-language phrase. |
| 3 | **Fill the gap:** the phrase with one key word replaced by `____`. |
| 2 | **What does it mean:** three meanings in the user language, of which one is correct. The wrong options are plausible but clearly different. |
| 1 | **Which situation:** describe an everyday situation; the learner picks the phrase from the sheet that fits it. |

More rules:

- If the sheet has fewer than 5 phrases, use each phrase for more than one question type, so that there are still 10 questions.
- Each answer names the phrase number and its timestamp, so the learner can replay the scene.
- Answers come after all questions, under their own heading.

## Excerpt limits

| Item | Limit |
|---|---|
| Phrase | at most 12 words |
| Context line | at most 15 words |
| Total quoted text per phrase block | at most three lines |

The sheet never contains the full subtitle file, and never contains whole scenes.
