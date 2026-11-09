# Phrase selection and alignment

Read this file in steps 4 to 6 of [SKILL.md](../SKILL.md). Every rule here works only on subtitle text that `file-agent` returned. Nothing here reads or writes NAS data.

## 1. Parse the subtitle text into cues

A cue is one subtitle entry. It has a start time, an end time and its text. Write every time as `HH:MM:SS.mmm`.

### SubRip (`.srt`)

Entries are separated by blank lines. Each entry has three parts:

1. a counter line;
2. a timing line;
3. one or more text lines.

```text
12
00:41:12,480 --> 00:41:15,020
Could you keep an eye on my bag?
```

How to parse:

- **Timing line:** read the start time before the arrow and the end time after it. The comma separates the milliseconds.
- **Formatting tags:** remove `<i>`, `<b>`, `<u>` and `<font ...>` tags. Keep the words inside them.
- **Several text lines:** join them with a space.

### Advanced SubStation (`.ass`, `.ssa`)

Use only the `[Events]` section:

1. The `Format:` line gives the field order.
2. Each `Dialogue:` line is one cue. Read its `Start`, `End` and `Text` fields.
3. `Text` is always the last field and may itself contain commas.

How to clean up:

- **Comments:** ignore `Comment:` lines.
- **Override blocks:** remove anything in curly braces that starts with a backslash, for example `{\i1}` or `{\pos(10,20)}`.
- **Line breaks:** replace `\N` and `\n` with a space.
- **Times:** they use `H:MM:SS.cc`, with hundredths of a second. Convert them to milliseconds.
- **Signs and lyrics:** drop a cue whose style name contains `sign`, `song`, `karaoke`, `OP` or `ED`.

### After parsing

- Sort cues by start time.
- If a sentence runs over two consecutive cues, merge them into one sentence that uses the first cue's start time. Treat it as running over when the first cue has no closing punctuation and the gap between the cues is under 0.5 s.
- Keep only cues whose start time is inside the scene range.
- **Unreadable text:** stop and report the file as unreadable if both of these are true:
  - more than 5 % of the characters are replacement marks or control characters;
  - no cue can be parsed.

  Do not repair or guess text.

## 2. Remove lines that are not worth learning

Drop a cue, or the part of a cue named below, when it is any of the following:

- **Names and places:**
  - a cue that is only a name or a place, such as "John!" or "Paris.";
  - a vocative name inside a phrase, such as "Nice to meet you, Mr. Grant". Remove the name and keep the useful part: "Nice to meet you".
- **Fillers:**
  - a one-word filler or interjection in any language, for example yeah, oh, uh, hmm, okay, hey, wow, yes, no, ja, oui, sí, はい or ええ;
  - a cue made only of fillers.
- **Sound and labels:**
  - sound descriptions in brackets or parentheses, such as "[door slams]" or "(laughs)";
  - speaker labels, such as "MAN:".
- **Music:** song lyrics, and cues marked with ♪ or #.
- **On-screen text:** signs, captions written in capitals, and numbers on their own.
- **Credits and adverts:** subtitle credits, adverts, web addresses and lines such as "Subtitles by", "Synced by" or "Support us".
- **Offensive language:**
  - slurs and sexual content;
  - mild informal or rude language, except at advanced level, where it may be kept with a register note.
- **Earlier sheets:** phrases already in the earlier sheet, when the user asked for new phrases.

## 3. Score the remaining candidates

Give each candidate three scores from 0 to 3.

### Usefulness

How often a learner could reuse the phrase in daily life outside this film.

- **High:**
  - greetings, requests, offers and apologies;
  - opinions, feelings, plans and directions;
  - shopping, time and small talk;
  - fixed expressions, collocations and phrasal verbs.
- **Zero:** lines that only make sense in the plot.

### Frequency

How often the phrase, or its core chunk, occurs in this title:

| Occurrences | Score |
|---|---|
| 1 | 0 |
| 2 | 1 |
| 3 to 4 | 2 |
| 5 or more | 3 |

Count exact matches and the same chunk with small changes, such as tense or pronoun. When two candidates tie, prefer the one that is more common in everyday speech.

### Level fit

| Level | Good fit |
|---|---|
| `beginner` | 2 to 6 words, very common words, simple present or past, polite everyday forms, no idioms. |
| `intermediate` | 3 to 10 words, phrasal verbs, common idioms, modal verbs, simple conditionals, informal but neutral register. |
| `advanced` | Up to 12 words, idioms, slang with a register note, irony and humour, complex grammar, cultural references. |

A phrase with level fit 0 is excluded.

Total = usefulness × 2 + frequency + level fit.

## 4. Choose the final list

1. Sort by total score.
2. Go down the list and keep a phrase only if all of these hold:
   - its core chunk is not already kept;
   - its scene-range part is not full. Split the scene range into five equal parts; one part may hold at most 35 % of `{COUNT}`, rounded up;
   - the kept list stays a mix of functions, so it is not all questions or all greetings.
3. Stop at `{COUNT}` phrases. If the candidates run out first, keep what there is and report the real number.

Keep for each phrase:

| Field | Rule |
|---|---|
| Phrase | The original wording, at most 12 words. If it was shortened, mark the cut with "…". |
| Start and end time | From the cue. |
| Line before and line after | The previous and next cue texts, each at most 15 words. |
| Reason | One short reason for choosing the phrase, used when writing the usage note. |

## 5. Alignment check between the two subtitle files

Run this check before any phrase is paired with a cue from the user-language file.

### Measure

1. Pick up to 20 anchor cues from the target-language file. Spread them evenly over the scene range and choose cues longer than one second.
2. For each anchor, find the user-language cue whose start time is nearest and within 10 seconds. Accept it only if its duration is within 30 % of the anchor's duration.
3. Record each offset (user-language start minus target-language start).
4. Also compare the total number of cues in the two files over the same range.

### Decide

| Result | Condition | Action |
|---|---|---|
| Aligned | At least 8 anchors matched, median offset within ±0.5 s, and largest minus smallest offset at most 1.0 s. | Pair by timestamp. |
| Constant offset | At least 8 anchors matched, largest minus smallest offset at most 1.0 s, but median offset larger than ±0.5 s. | Shift every user-language cue by minus the median offset. Tell the user the offset in seconds, then pair by timestamp. |
| Misaligned | Fewer than 8 anchors matched, or the offsets spread more than 1.0 s (drift), or the cue counts differ by more than 30 %. | Do not pair by timestamp. Report the measured numbers and follow step 6 of SKILL.md. |

### Pair

For each phrase, the translation is the user-language cue or cues that overlap the phrase's time window, widened by 0.5 s on each side.

- If several cues overlap, join them in time order.
- If the joined text clearly does not mean the same thing as the phrase, treat the phrase as unmatched. It is then translated by the NAS translation capability in step 6. Never write a translation yourself.
- Subtitle translations translate the whole line, so mark them "subtitle line".
