---
name: subtitle-tutor
description: Language lessons from films and series already in the NAS media library. Finds the subtitles of a chosen title or of something recently watched, picks useful phrases for the learner level (beginner, intermediate or advanced), pairs each phrase with a translation and its exact timestamp, and saves a study sheet with context lines, usage notes and a 10-question self-quiz after confirmation, plus an optional flashcard file. Remembers earlier sheets so the next lesson brings new phrases and a short review. Use when the user says things like "make a Spanish lesson from Charade", "teach me French phrases from the film I watched last night", "turn season 1 episode 3 into a Japanese study sheet", or "which useful English lines are in this movie".
---

# Subtitle Tutor

Version 1.1.0. Subtitle Tutor turns a film or series the user already owns on the NAS into a language lesson. It reads the subtitles, chooses the phrases most worth learning at the user's level, and pairs each phrase with a translation and the exact moment it is spoken. It then writes a study sheet next to the user's other notes. Every NAS operation is done by the registered NAS experts listed below. Choosing phrases, writing notes and building the quiz are reasoning by the NAS assistant over the real text the experts return.

# Goal

The user receives one Markdown study sheet for one title (or one episode), in one target language and at one level. The sheet contains:

- the requested number of phrases (default 20), each with:
  - a translation into the user's language
  - the start timestamp
  - the line spoken before and the line spoken after
  - a short usage note
- a 10-question self-quiz with an answer key. When the user has studied this title before, up to 3 questions review phrases from the latest earlier sheet.

The sheet is saved only after the user confirms, in `Language Lessons/{TITLE_SAFE}/` inside the user's personal folder or in another folder the user names. On request, a flashcard file (tab-separated text) is saved next to it.

Scope:

- Only video files and subtitle files already on the NAS, plus subtitles downloaded with explicit confirmation.
- Only external subtitle files in SubRip (`.srt`) or Advanced SubStation (`.ass`, `.ssa`) format. Subtitle tracks embedded inside a video file are out of scope.
- The Skill never deletes or moves files, never shares anything outside the NAS, and never changes the video file itself.

# Required input

Ask for any missing required item in one short message. Do not ask for anything else.

| Input | Required | Default and rules |
|---|---|---|
| Title of the film or series | yes, unless the user means something recently watched | Free text, as the user calls it. "The film I watched last night" or "my last episode" starts from recently watched titles (step 2). |
| Season and episode | only for a series | Ask after step 2 if the match is a series and they were not given. |
| Target language (the language to learn) | yes | Language name; also record its ISO 639-1 code, for example Spanish = `es`. |
| User language (for translations and notes) | yes | If not stated, use the language of the user's message and say so in the summary. |
| Level | no | `beginner`, `intermediate` or `advanced`; default `intermediate`. |
| Number of phrases | no | Default 20; allowed 5 to 40. Set values outside the range to the nearest limit and tell the user. |
| Scene range | no | A start and end time such as 00:20:00 to 00:45:00, or "first 30 minutes". Default: the whole title. |
| Destination folder | no | Default: `Language Lessons/{TITLE_SAFE}` inside the user's personal folder. |

Before step 2, repeat the inputs back in one line, for example: "Spanish phrases from Charade, intermediate, 20 phrases, whole film, translations into English". Then continue without waiting, unless something is missing.

# Runtime values

These values are filled while the Skill runs; they are not placeholders for the author. Each gets its real value from the step named below before any instruction that uses it is sent.

- If a value is still unknown, do not send the instruction. Stop at that step and report what is missing.
- Experts never see the conversation. Write every value out in full inside the instruction, including the whole of `{SHEET_TEXT}`, `{CARDS_TEXT}` and `{LINES}`. A name in curly braces or a reference such as "the sheet above" would make the expert save or translate the wrong text.
- An instruction is one single-quoted string, so a filled value must not contain the straight single quote ('). Write every apostrophe in a value, including inside `{SHEET_TEXT}`, `{CARDS_TEXT}` and translations returned by an expert, as the typographic apostrophe (’). This is the only change allowed to copied subtitle text.
- Send one delegate command at a time and wait for its result before the next one.

| Value | Filled from |
|---|---|
| `{TITLE}` | User input. After step 2, the exact title returned by `media-agent`. |
| `{TITLE_SAFE}` | `{TITLE}` with each slash, backslash, colon, asterisk, question mark, double quote, angle bracket and vertical bar replaced by `-`. |
| `{SEASON}`, `{EPISODE}` | User input or the chosen recently watched item (series only); `0` and `0` for a movie. |
| `{EP_TAG}` | `S01E03` style for a series episode; empty for a movie. |
| `{TARGET_LANG}`, `{TARGET_CODE}`, `{USER_LANG}`, `{USER_CODE}` | User input, or the language of the user's message for the user language. |
| `{LEVEL}`, `{COUNT}`, `{RANGE}` | User input or defaults. |
| `{MEDIA_ID}`, `{VIDEO_PATH}` | Step 2: media ID and real file path returned by `media-agent` or `file-agent`. |
| `{VIDEO_DIR}` | The folder part of `{VIDEO_PATH}`. |
| `{USER_FOLDER}` | Step 2: folder the user typed, only when the media library gave no file path. |
| `{HOME_DIR}`, `{LESSON_DIR}` | Step 4: real personal folder path from `file-agent`, joined with `Language Lessons/{TITLE_SAFE}`; or the folder the user named. |
| `{SUB_PATH}`, `{TARGET_SUB}`, `{USER_SUB}` | Step 3: real paths of subtitle files returned by `file-agent`. |
| `{LANG_NAME}`, `{LANG_CODE}`, `{SUB_FILE_ID}`, `{DOWNLOADED_PATH}` | Step 3: language being searched, the `file-id` the user picked, the saved path if one was reported. |
| `{OLD_SHEET_PATH}` | Step 4: real path of the latest earlier sheet for this title and target language. |
| `{ALIGNMENT_LINE}` | Step 6: the one-line result of the alignment check, with the measured numbers. |
| `{LINES}` | Step 6: numbered phrases that still need a translation. |
| `{SHEET_NAME}`, `{SHEET_TEXT}` | Step 7: file name from [references/study-sheet-format.md](references/study-sheet-format.md) and the finished sheet. |
| `{CARDS_NAME}`, `{CARDS_TEXT}` | Step 7: flashcard file name and text, only if the user asked for flashcards. |
| `{TAG_NAME}` | Step 9: `studied: {TARGET_LANG} {LEVEL}` with the language name, for example `studied: Spanish intermediate`. |

# Workflow

The Skill hands every NAS operation to a registered expert with a standard delegate command and never runs NAS commands itself. Each step uses only the real result returned by an expert in an earlier step, never a guessed path, ID or text.

| Step | Expert | Catalog capability the expert is expected to use |
|---|---|---|
| 2 Find the title or a recently watched item | `media-agent`, `file-agent` | `ug-video` `search`; `ug-filesystem` `find` |
| 3 Find or download subtitles | `file-agent`, `media-agent` | `ug-filesystem` `ls`, `stat`, `cat`; `ug-filemgr` `tag-get-file`; `ug-video` `subtitle-search`, `subtitle-download` |
| 4 Read subtitles and earlier sheets | `file-agent` | `file-workflow` `get-user-dir`; `ug-filesystem` `ls`, `cat` |
| 6 Translate unmatched phrases | `document-agent` | `ug-document` `translate` |
| 7 Save the sheet and flashcards | `file-agent`, `knowledge-agent` | `ug-filesystem` `stat`, `mkdir`; `ug-knowledge` `save-text` |
| 8 Replay | `media-agent` | `ug-video` `search` (play) |
| 9 Tag the video | `file-agent` | `ug-filemgr` `tag-get-by-name`, `tag-add`, `tag-add-file` |

## Step 1: Collect input

Collect the inputs described in Required input and repeat them back in one line.

## Step 2: Find the title (read only)

1. If the user means something recently watched, send:

   `delegate --target media-agent --instruction 'List the 10 movies and TV episodes the current user watched most recently in the NAS video library, newest first. Read only: do not start playback and do not change anything. For each return the exact title, the year, movie or series, season and episode if any, the media ID and the real file path. If there are no results, return an empty list and say so.'`

   Show the list and ask which one to use (`waiting_user`). With no results, say that no recently watched title was found and ask for a title instead.

2. Otherwise send:

   `delegate --target media-agent --instruction 'Search the NAS video library for movies and TV series whose title matches {TITLE}. Read only: do not start playback and do not change anything. For every match return the exact title, the year, whether it is a movie or a series, the media ID, and the real file path of the video file. If there are no results, return an empty list and say so. Do not return similar or unrelated titles as matches.'`

3. Count a returned item as a match only if its title equals or contains {TITLE}, ignoring case and punctuation. If every returned title is clearly different, treat the result as no results.
   - **No results:** say "I could not find a title matching {TITLE} in the NAS media library." Stop. Do not offer other titles; the user may ask again with another title.
   - **One match:** use it.
   - **Several matches:** list them (title, year, movie or series, folder) and ask the user to choose (`waiting_user`).
4. If the chosen match is a series, get `{SEASON}` and `{EPISODE}` from the user if they are missing, then send:

   `delegate --target media-agent --instruction 'For the TV series with media ID {MEDIA_ID} ({TITLE}), return the real file path of season {SEASON} episode {EPISODE}. Read only. If that episode is not in the library, say so and return no path. Do not return a different episode.'`

   If no path comes back, say that the episode is not in the library and stop.
5. If the media library returned the title but no real file path, ask which NAS folder holds the video and record the answer as `{USER_FOLDER}`. Then send:

   `delegate --target file-agent --instruction 'In the folder {USER_FOLDER} and its subfolders up to two levels deep, find video files whose file name contains {TITLE}, ignoring upper and lower case. Read only. Return the real path, size and modification time of each match. If there are no results, return an empty list and say so.'`

   With no results, say that no video file for {TITLE} was found there and stop. With several, ask the user to choose.
6. Record `{MEDIA_ID}`, `{VIDEO_PATH}`, `{VIDEO_DIR}` and, for a series, `{EP_TAG}`.

## Step 3: Find the subtitles (read only unless the user confirms a download)

1. Send:

   `delegate --target file-agent --instruction 'List the files directly inside the folder {VIDEO_DIR}, without going into subfolders. Read only. Return the name, real path, size and modification time of every file whose name ends in .srt, .ass or .ssa, in upper or lower case. Also return the tags currently attached to the video file {VIDEO_PATH}. If the folder has no subtitle files, return an empty list and say so.'`

   Keep this list; it is the before-download snapshot. For a series, keep only files whose name contains the same season and episode marker as the video file.
2. Work out the language of each subtitle file:
   - First use a language tag in the file name, for example `.en.`, `.eng.`, `.es.`, `.spa.`, `.ja.`, `.jpn.`, `English` or `Español`.
   - If the name has no tag, set `{SUB_PATH}` to that file and send:

     `delegate --target file-agent --instruction 'Read the first 3000 bytes of the text file {SUB_PATH} and return them exactly as stored, without summarising or changing anything. Read only.'`

     Identify the language from the returned text.
   - If two files share a language, prefer the one whose base name matches the video file; otherwise ask the user.
   - Record `{TARGET_SUB}` and `{USER_SUB}`.
3. If a subtitle file is missing for the target language, the user language or both:
   - Say exactly which language is missing.
   - Ask: "Shall I search for {LANG_NAME} subtitles online? This uses the NAS video service to contact an online subtitle source outside the NAS. The film's details are sent to that source and one subtitle file is downloaded into the video folder. Nothing else is sent." Ask once per missing language; continue only on a clear yes.
   - **If the user declines:** without target-language subtitles, say a lesson cannot be built and stop. Without user-language subtitles, continue; step 6 then uses the translation capability.
4. For each missing language the user approved:
   1. Set `{LANG_NAME}` and `{LANG_CODE}`, then send:

      `delegate --target media-agent --instruction 'Search online subtitles for the video {VIDEO_PATH} in {LANG_NAME} ({LANG_CODE}). Use season {SEASON} and episode {EPISODE}; both are 0 for a movie. Search only: do not download anything. Return up to 10 candidates with their file-id, file name, language, format and release or version name. If there are no results in this language, return an empty list and say so. Do not return other languages.'`

   2. **No results:** say "No {LANG_NAME} subtitles were found online for {TITLE}." Then apply the decline rule above.
   3. **Candidates found:** show at most five, first those whose release name matches the video file name (a matching release lowers the risk of misaligned timings). Ask the user to pick one and to confirm the download (`waiting_user`). Record the chosen `file-id` as `{SUB_FILE_ID}`.
   4. Only after the user confirms, send:

      `delegate --target media-agent --instruction 'Download the subtitle with file-id {SUB_FILE_ID} for the video {VIDEO_PATH}. The user has confirmed this download from an online source outside the NAS. Download only this one file. Do not change, move or remove any other file. Return the download status and, if known, the saved file path.'`

      The NAS may show its own approval prompt (`waiting_approval`).
   5. After `completed`, send the listing instruction from item 1 of this step again. The downloaded file is a path that is in the new list but not in the snapshot.
   6. If the comparison finds nothing but the download reported a saved path, record it as `{DOWNLOADED_PATH}` and send:

      `delegate --target file-agent --instruction 'Check whether the file {DOWNLOADED_PATH} exists. Read only. Return its real path, size and modification time, or say that it does not exist.'`

   7. Exactly one new subtitle file confirmed: use it. None: say "The download was reported, but no new subtitle file could be found" and apply the decline rule. Several: ask which one to use.

## Step 4: Read any earlier sheet, then the subtitles (read only)

Items 1 and 2 come first, before any subtitle text is read, also for a first lesson. The folder listing is the only way to find earlier lessons and existing file names.

1. Find the destination. Send:

   `delegate --target file-agent --instruction 'Return the real path of the personal folder of the current user. Read only. Do not create or change anything.'`

   Record `{HOME_DIR}` and set `{LESSON_DIR}`, unless the user named another folder.
2. List the lesson folder. Send:

   `delegate --target file-agent --instruction 'Check whether the folder {LESSON_DIR} exists. If it exists, list the files directly inside it with name, real path and modification time. Read only. Do not create or change anything. If the folder does not exist or is empty, say so.'`

3. If the listing holds earlier sheets for this title and target language (their names contain `{TITLE_SAFE}` and `{TARGET_LANG}` and end in `.md`), set `{OLD_SHEET_PATH}` to the newest one and send:

   `delegate --target file-agent --instruction 'Read the text file {OLD_SHEET_PATH} and return its content exactly as stored, without summarising or changing anything. Read only.'`

   Tell the user which earlier sheet was found. Its phrases are excluded from step 5, and up to 3 of them go into the review questions in step 7.
4. Set `{SUB_PATH}` to `{TARGET_SUB}` and send the instruction below; then do the same for `{USER_SUB}` if it exists.

   `delegate --target file-agent --instruction 'Read the whole text file {SUB_PATH} and return its content exactly as stored, without summarising, translating or removing lines. Read it in consecutive chunks of 65536 bytes starting at offset 0 until the end of the file. Return the chunks in order, with the total size in bytes. Read only. If a chunk cannot be read, return the chunks already read and say at which offset reading stopped.'`

5. Parse the text into cues following [references/phrase-selection.md](references/phrase-selection.md) and keep only cues inside `{RANGE}`.
   - Zero cues in the target file, or unreadable text: say so and stop. Do not guess the content.
   - Encoding problems (replacement marks in more than 1 % of the characters): name the file and the problem, and ask whether to continue with the readable lines or stop.
   - Reading stopped part-way: tell the user which time span was read and ask whether to continue with it.

## Step 5: Choose the phrases part by part (reasoning over the real subtitle text)

The phrases must come from the whole scene range, not from the opening scenes. Choose `{COUNT}` phrases from the target-language cues in this order:

1. Split the scene range into five equal parts by time, from the first cue's start to the last cue's end, and write down the five time spans.
2. Take the parts one at a time. Look only at the cues inside the current part and pick its best phrases: about a fifth of `{COUNT}`, never more than 35 % of `{COUNT}`. Do this for all five parts, including the last one.
3. If a part has too few good candidates, take the missing phrases from the neighbouring parts.
4. Put the final list in timestamp order. For each phrase, copy from the subtitle text as returned: its cue's timing line and text, and the cues before and after it. Write the sheet from these copies, never from memory. Count the phrases per part again; these counts go into the sheet's "Phrases per fifth" row.

Within each part, choose with the rules in [references/phrase-selection.md](references/phrase-selection.md): level fit, everyday usefulness and frequency in this title. For more than 300 cues, work in blocks of 300 and keep at most twice `{COUNT}` candidates from each block before choosing the final list.

Each phrase's time is the start time on its own cue's timing line in the target-language file. Copy it; never estimate it, and never take a time from the user-language file.

Never select names or places on their own, one-word fillers, sound descriptions, song lyrics, on-screen signs, subtitle credits or advertising lines, slurs, or phrases already in the earlier sheet. Leave out a name used to address someone and keep the rest of the line. Keep excerpts short: at most 12 words per phrase and at most 15 words per context line. Copy phrases and context lines character for character from their cues; never drop or change words inside them.

If fewer suitable phrases exist than requested, select all of them and tell the user the real number (a partial result).

## Step 6: Pair each phrase with a translation

1. If `{USER_SUB}` exists, run the alignment check in [references/phrase-selection.md](references/phrase-selection.md) every time, even when the timings look identical: pick 10 anchors, one from each tenth of the scene range; quote each anchor and the user-language line that says the same thing; compute each difference from the two timing lines. Never assume a result without measuring, and never fill a row without a quoted user-language line. Record `{ALIGNMENT_LINE}` from the measured numbers in this form: "Alignment check: {N} of 10 anchors matched, median difference {M} s, spread {S} s: {RESULT}." Show the user this line together with the anchor table, all 10 rows: right away when the result is misaligned, otherwise in the preview of step 7. There are three outcomes:
   - **Aligned:** pair each phrase with the user-language cue at the same time that says the same thing; mark it "subtitle line".
   - **Constant offset:** shift the user-language cues by the measured offset, say the offset in seconds, then pair as above.
   - **Misaligned** (different versions, cuts or frame rates): say so with the measured numbers and do not pair by timestamp. Offer three choices: translate the phrases with the NAS translation capability, choose or download another user-language subtitle (back to step 3), or stop.
2. Phrases still without a translation go into `{LINES}` as numbered lines (at most 40 per instruction):

   `delegate --target document-agent --instruction 'Translate the following numbered lines from {TARGET_LANG} ({TARGET_CODE}) into {USER_LANG} ({USER_CODE}). Translate the given text only: there is no source file. Do not save an output file. Return the translation of each line with its number, in the same order, and nothing else. If this language pair is not supported, say so and return failed instead of guessing. Lines: {LINES}'`

   The NAS may ask for approval (`waiting_approval`). Mark these translations "machine translation". If the expert reports an `output_file`, tell the user its path.
3. If translation returns `failed` because the pair is not supported, say right away, in its own message: "The NAS translation capability does not support {TARGET_LANG} to {USER_LANG}." Never invent a translation. Offer to save the sheet with those phrases marked "no translation available", or to stop (`waiting_user`).

## Step 7: Write the study sheet and save it after confirmation

1. Write `{SHEET_TEXT}` exactly in the format of [references/study-sheet-format.md](references/study-sheet-format.md), including the self-quiz, the review questions when an earlier sheet exists, the source files, the alignment result and any flags. [references/example-sheet.md](references/example-sheet.md) shows a finished sheet. Every time the sheet is written out, in the conversation or inside a save instruction, first check it against the subtitle text:
   - each phrase and context line, word by word, against its cue, and each "subtitle line" translation against its user-language cue; fix any word that differs;
   - each phrase without a name used to address someone, and none that is a single word or filler;
   - each time against its cue's timing line in the target-language file;
   - the "Phrases per fifth" numbers, counted again from the times written on the sheet;
   - each "Fill the gap" and "What does it mean" question, which must quote target-language text;
   - each question, which must not contain its answer, an "(answer: …)" note or a hint;
   - each "Say it" answer, which is the target-language phrase as written on the sheet;
   - the quiz: exactly 10 questions, with "(review)" questions only when an earlier sheet was read in step 4.
2. Pick `{SHEET_NAME}` so that it does not match a file listed in step 4.
3. Show the user, in one message: `{ALIGNMENT_LINE}` from step 6 with its anchor table, the earlier sheet used for review (if any), the phrase list with one line per phrase (number, time, phrase, translation), the full destination `{LESSON_DIR}/{SHEET_NAME}`, and whether the folder will be created. Do not paste the whole sheet. Ask: "Save the study sheet here? Reply yes, yes with flashcards, or no." (`waiting_user`) This question is never the end of the task: wait for the answer. The sheet saved or shown later uses exactly the phrases, times and translations of this list.
   - **No:** write the whole sheet out in the conversation instead and stop. Nothing is written to the NAS.
   - **A different folder:** use the folder the user names and repeat step 4 items 2 and 3 for it.
   - **Yes:** do not ask again. Send the instructions below one at a time, each after the previous result: the folder (item 4), the name check (item 5), the sheet (item 6).
   - **Yes with flashcards:** the same, then the flashcards (item 7). The flashcard save is part of the job: send it before the tag question.
4. If `{LESSON_DIR}` does not exist, send:

   `delegate --target file-agent --instruction 'Create the folder {LESSON_DIR}, including missing parent folders. The user has confirmed this. Do not change, move or remove anything else. Return the real path of the created folder.'`

5. If `{LESSON_DIR}` already existed, send this just before saving:

   `delegate --target file-agent --instruction 'Check whether a file named {SHEET_NAME} exists in the folder {LESSON_DIR}. Read only. Return yes or no and, if yes, its real path and modification time.'`

   If it exists, ask the user to choose a new name (recommended; adds ` (2)`), replacing the existing file, or cancel. Replace only after an explicit "replace".
6. Send one of these:
   - **New file (normal case):**

     `delegate --target knowledge-agent --instruction 'Save the following Markdown text as a new file named {SHEET_NAME} in the folder {LESSON_DIR}. The user has confirmed this save. Do not replace an existing file, and do not change any other file. Return the real output file path, the byte count and whether the save was verified. Text: {SHEET_TEXT}'`

   - **Replace (only after an explicit "replace" in item 5):**

     `delegate --target knowledge-agent --instruction 'Save the following Markdown text as the file {SHEET_NAME} in the folder {LESSON_DIR}, replacing the existing file of the same name. The user has explicitly confirmed replacing it. Do not change any other file. Return the real output file path, the byte count and whether the save was verified. Text: {SHEET_TEXT}'`

   After `Text:` comes the complete sheet, from its first heading to its last note, written out in the instruction itself.

   The NAS may ask for approval (`waiting_approval`). Report the save as done only when the result is `completed` with a verified save and a real output path, and give the user that path.
7. If the user chose "yes with flashcards", build `{CARDS_NAME}` and `{CARDS_TEXT}` as described in [references/study-sheet-format.md](references/study-sheet-format.md) and send:

   `delegate --target knowledge-agent --instruction 'Save the following plain text as a new file named {CARDS_NAME} in the folder {LESSON_DIR}. The user has confirmed this save. Keep every tab character and line break exactly as given. Do not replace an existing file, and do not change any other file. Return the real output file path, the byte count and whether the save was verified. Text: {CARDS_TEXT}'`

   A failed flashcard save does not affect the saved sheet; report it separately.
8. After the verified sheet save, and after the flashcard result when flashcards were requested, ask the tag question of step 9. The final report comes after the user's answer to it.

## Step 8: Replay a phrase (optional, on request)

When the user asks to replay a phrase (for example "replay phrase 7"):

1. Give its timestamp minus two seconds as a lead-in, with the line before and the line after.
2. Explain that the NAS video controls available to this Skill cannot jump to a time, so the user seeks to that time in the player.
3. Offer to start the title. On yes, send:

   `delegate --target media-agent --instruction 'Start playback of the video with media ID {MEDIA_ID} ({TITLE}) in the NAS video player. The user asked for this. Do not change anything else. Return whether playback started and on which player.'`

   If playback does not start, say so and give the timestamp only.

## Step 9: Tag the video as studied (always offered once after a verified save)

1. Ask once: "Tag the video file with {TAG_NAME} so you can see later that you studied it?" Continue only on yes.
2. Send:

   `delegate --target file-agent --instruction 'Attach the tag named {TAG_NAME} to the video file {VIDEO_PATH}. The user has confirmed this. First look up an existing tag with exactly this name, and create the tag only if none exists. Do not remove or change any other tag or file. Return the tag ID and whether the tag is now attached to the file.'`

   The NAS may ask for approval (`waiting_approval`).
3. If the tag name is rejected, report the exact reason. Offer `studied-{TARGET_CODE}-{LEVEL}` as an alternative and use it only after the user agrees.

# Completion and failure

## Delegation states

| State | What the Skill does |
|---|---|
| `completed` | Use only the real result data. Check that the fields the next step needs are present, for example a real path or a `file-id`. If a needed field is missing, treat the step as `failed`. |
| `failed` | Tell the user in plain words which step failed and the reason the expert gave. Stop every step that depends on it. Keep and report the results already obtained. Do not retry with guessed values. |
| `cancelled` | Say what was cancelled and what was not done, for example "Nothing was downloaded" or "The sheet was not saved". Stop that branch. |
| `waiting_user` | Pass the expert's question to the user unchanged, wait for the answer, and send it back. Do not answer for the user. |
| `waiting_approval` | Tell the user what is waiting for approval: a download from outside the NAS, a new folder, a save, a translation or a tag. Wait for the approval result. If approval is refused, treat the step as `cancelled`. |

## Failure catalogue

| Situation | Message and behaviour |
|---|---|
| Title not found | "No title matching {TITLE} is in the NAS media library." Stop. No similar titles are offered as substitutes. |
| Nothing recently watched | Say so and ask for a title. |
| Series episode not found | Say which episode is missing. Stop. |
| No subtitles at all | Local files and online search gave no results, or the user declined the download. Say so and stop. Embedded subtitle tracks are not used. |
| Target-language subtitles missing | A lesson cannot be built. Stop after saying which language is missing. |
| User-language subtitles missing | Continue with the NAS translation capability; mark every translation "machine translation". |
| Unsupported language pair | Say the pair is not supported. Offer to save without translations (clearly marked) or stop. Never guess. |
| Misaligned subtitle versions | Show the anchor numbers. Offer translation, another subtitle file, or stop. |
| Unreadable, wrongly encoded or empty subtitle file | Name the file and the problem. Stop if it is the target-language file and nothing readable remains. |
| Partial read | Report the time span that was read and ask whether to continue with it. |
| Fewer phrases than requested | Deliver the real number and say so. |
| Folder creation or save failed | Report the reason. Show the sheet in the conversation so no work is lost. Do not write it elsewhere without asking. |
| Flashcard save or tag failed | Report the reason. The saved sheet is not affected. |
| Playback not available | Give the timestamp only. |

## Final report

End with a short report: the title and subtitle files used; the number of phrases, with how many were translated by subtitle and how many by machine; the alignment result; the earlier sheet used for review, if any; the saved file paths, each only if its own save instruction returned `completed` with a verified save (a file whose save was never sent was not saved); whether the tag was added; and anything that was skipped or failed.

# Privacy and data flow

- **Stays on the NAS:** the video files, the subtitle files, the study sheets, the flashcard files and the tags. The Skill reads only the chosen video folder, a folder the user names to locate the video, the recently watched list when asked, and the lesson folder with its earlier sheets.
- **The only outside connection the Skill makes is the optional subtitle search and download.** It goes through the NAS video service and only after the user's explicit yes. The user is told beforehand that it contacts an online subtitle source outside the NAS.
- **The assistant's model:** phrase choice, notes and the quiz are worked out by the model the NAS assistant uses. If the user has set the assistant to a cloud model, the subtitle lines it reads are handled under the assistant's own settings. The Skill adds no AI service of its own.
- **Nothing is shared or sent anywhere else.** The Skill has no sharing step.
- **The sheet is for personal study.** It keeps only short excerpts: at most 12 words per phrase and at most 15 words per context line.
- **No account data, passwords or keys** are requested or stored.

# Generation-time capability evidence

Catalog: `uliya-skill-kit` 0.7.3, `data/capability-catalog.json`, version 2.0.0. Each CLI has one owning expert:

- `ug-video` → `media-agent`
- `ug-filesystem` → `file-agent`
- `ug-filemgr` → `file-agent`
- `file-workflow` → `file-agent`
- `ug-document` → `document-agent`
- `ug-knowledge` → `knowledge-agent`

Not available in the catalog, and therefore not claimed: seeking a video to a timestamp (`ug-video` `control` offers only pause, continue, next and previous), a published list of translation language pairs, and reading subtitle tracks embedded inside a video file.

# References

- [references/phrase-selection.md](references/phrase-selection.md): subtitle parsing, phrase selection by level, and the alignment check.
- [references/study-sheet-format.md](references/study-sheet-format.md): sheet and flashcard layout, file names, usage notes, quiz and review rules.
- [references/example-sheet.md](references/example-sheet.md): a finished example sheet made from original test subtitles.
- [references/install-and-testing.md](references/install-and-testing.md): install, setup, removal and a quick test.
- [references/disclosures.md](references/disclosures.md): third-party components and licences, functionality built for the UGREEN Hackathon 2026, AI tools used, and version history.
