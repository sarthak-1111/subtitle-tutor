# Phrase selection and alignment

Read this file in steps 4 to 6 of [SKILL.md](../SKILL.md). Every rule here works only on subtitle text that `file-agent` returned. Nothing here reads or writes NAS data.

## 1. Parse the subtitle text into cues

A cue is one subtitle entry: a start time, an end time and its text. Write every time as `HH:MM:SS.mmm` when reasoning and as `HH:MM:SS` on the sheet.

### SubRip (`.srt`)

Entries are separated by blank lines. Each entry has a counter line, a timing line and one or more text lines.

```text
12
00:41:12,480 --> 00:41:15,020
Could you keep an eye on my bag?
```

- **Timing line:** the start time is before the arrow and the end time after it. The comma separates the milliseconds.
- **Formatting tags:** remove `<i>`, `<b>`, `<u>` and `<font ...>` tags; keep the words inside them.
- **Several text lines:** join them with a space.

### Advanced SubStation (`.ass`, `.ssa`)

Use only the `[Events]` section. The `Format:` line gives the field order. Each `Dialogue:` line is one cue: read its `Start`, `End`, `Style` and `Text` fields. `Text` is the last field and may itself contain commas.

- **Comments:** ignore `Comment:` lines.
- **Override blocks:** remove anything in curly braces that starts with a backslash, for example `{\i1}` or `{\pos(960,80)}`.
- **Line breaks:** replace `\N` and `\n` with a space.
- **Times:** they use `H:MM:SS.cc` (hundredths of a second); convert to milliseconds.
- **Signs and lyrics:** drop a cue whose style name contains `sign`, `song`, `karaoke`, `OP` or `ED`, in any case.

### After parsing

- Sort cues by start time.
- If a sentence runs over two consecutive cues (the first has no closing punctuation and the gap is under 0.5 s), merge them into one sentence with the first cue's start time.
- Keep only cues whose start time is inside the scene range.
- **Encoding:** count replacement characters (Unicode U+FFFD, usually shown as a question mark in a black diamond) and control characters. Above 1 % of the characters, report an encoding problem in that file and ask whether to continue with the readable lines. If no cue can be parsed at all, the file is unreadable. Never repair or guess text.

### Long files

A feature film usually has 1,000 to 2,000 cues. With more than 300 cues in the scene range, work through them in blocks of 300 in time order. From each block keep at most twice `{COUNT}` candidates with their scores, then choose the final list from all kept candidates. This keeps each reasoning step small enough for the NAS model.

## 2. Remove lines that are not worth learning

Drop a cue, or the part of a cue named below, when it is any of the following:

- **Names and places:** a cue that is only a name or a place ("¡Anna!", "Paris."). In a phrase with a vocative name ("Nice to meet you, Mr. Grant"), remove the name and keep the useful part ("Nice to meet you").
- **Fillers:** a one-word filler or interjection in any language (yeah, oh, uh, hmm, okay, hey, wow, yes, no, eh, ajá, mmm, ja, oui, sí, はい, ええ), or a cue made only of fillers.
- **Sound and labels:** sound descriptions in brackets or parentheses ("[door slams]", "(laughs)"); speaker labels at the start of a line ("MAN:", "ANNA:"), which are removed while the rest of the line is kept.
- **Music:** song lyrics and cues marked with ♪ or #.
- **On-screen text:** signs, captions written in capitals, and numbers on their own.
- **Credits and adverts:** subtitle credits, adverts, web addresses, and lines such as "Subtitles by", "Synced by", "Subtítulos:" or "Support us".
- **Offensive language:** slurs and sexual content always; mild informal or rude language except at advanced level, where it may be kept with a register note.
- **Earlier sheets:** phrases already in the earlier sheet read in step 4.

## 3. Score the remaining candidates

Give each candidate three scores from 0 to 3.

### Usefulness

How often a learner could reuse the phrase in daily life outside this film.

- **High:** greetings, requests, offers, apologies, thanks; opinions, feelings, plans, directions; shopping, prices, time, health, small talk; fixed expressions, collocations and phrasal verbs.
- **Zero:** lines that only make sense in the plot.

### Frequency

How often the phrase, or its core chunk, occurs in this title (exact matches and the same chunk with small changes such as tense or pronoun):

| Occurrences | Score |
|---|---|
| 1 | 0 |
| 2 | 1 |
| 3 to 4 | 2 |
| 5 or more | 3 |

When two candidates tie, prefer the one that is more common in everyday speech.

### Level fit

| Level | Good fit |
|---|---|
| `beginner` | 2 to 6 words, very common words, simple present or past, polite everyday forms, no idioms. |
| `intermediate` | 3 to 10 words, phrasal verbs, common idioms, modal verbs, simple conditionals, informal but neutral register. |
| `advanced` | Up to 12 words, idioms, slang with a register note, irony and humour, complex grammar, cultural references. |

A phrase with level fit 0 is excluded. Total = usefulness × 2 + frequency + level fit.

## 4. Choose the final list

1. Split the scene range into five equal parts by time, from the first cue's start to the last cue's end.
2. In each part, sort the candidates by total score and keep the best ones, about a fifth of `{COUNT}` per part. One part may hold at most 35 % of `{COUNT}`, rounded up. Keep a phrase only if:
   - its core chunk is not already kept;
   - the kept list stays a mix of functions (not all questions, not all greetings).
3. If a part runs out of good candidates, take the next best ones from the neighbouring parts.
4. Stop at `{COUNT}` phrases. If the candidates run out first, keep what there is and report the real number.

Keep for each phrase:

| Field | Rule |
|---|---|
| Phrase | The original wording, copied exactly from the cue, at most 12 words. If shortened, mark the cut with "…". |
| Start time | Copied from the timing line of the target-language cue the phrase comes from; never from the user-language file. |
| Line before and line after | The previous and next cue texts, copied exactly, each at most 15 words. |
| Reason | One short reason for choosing it, used for the usage note. |

## 5. Alignment check between the two subtitle files

Run this before pairing any phrase with a cue from the user-language file. Translations of the same film often split lines differently, so anchors are matched by meaning, not by the nearest timestamp.

### Measure

1. Split the scene range into ten equal parts by time. From each part pick one anchor cue in the target-language file: a clear, distinctive line of more than three words. If a part has no such line, take one from the nearest part.
2. For each anchor, find the user-language cue that says the same thing (it translates the anchor) and starts within 30 seconds of it. If there is none, the anchor is unmatched.
3. Write a table with both lines quoted. Copy each start time from its own file's timing line. The difference is the user-language start minus the target-language start, in seconds with one decimal. An unmatched anchor gets "none" and no difference; never copy the target start into the user column.

Example from a file pair whose English subtitles run 1.5 s late:

| # | Target start | Target line | User start | User line | Difference (s) |
|---|---|---|---|---|---|
| 1 | 00:01:09.4 | Aller simple ou aller-retour ? | 00:01:10.9 | One way or return? | +1.5 |
| 2 | 00:04:02.7 | Vous avez une pièce d’identité ? | none | none | none |
| … | … | … | … | … | … |

4. Also compare the number of cues in the two files over the same range.

### Decide

| Result | Condition | Action |
|---|---|---|
| Aligned | At least 7 anchors matched, every difference within ±0.5 s. | Pair by timestamp. |
| Constant offset | At least 7 anchors matched, largest minus smallest difference at most 1.0 s, but the median difference beyond ±0.5 s. | Subtract the median difference from every user-language time, tell the user the offset in seconds, then pair by timestamp. |
| Misaligned | Fewer than 7 anchors matched, or the differences spread more than 1.0 s (drift), or the cue counts differ by more than 30 %. | Do not pair by timestamp. Report the measured numbers and follow step 6 of SKILL.md. |

### Pair

For each phrase, the translation is the user-language cue (after any offset correction) that overlaps the phrase's time window and says the same thing. If two cues together carry the meaning, join them in time order. If no overlapping cue clearly means the same as the phrase, treat the phrase as unmatched; it is translated by the NAS translation capability in step 6. Never write a translation yourself. Subtitle translations cover the whole line, so mark them "subtitle line".
