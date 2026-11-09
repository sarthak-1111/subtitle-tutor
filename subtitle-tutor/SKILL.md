---
name: subtitle-tutor
description: Language lessons from films and series already in the NAS media library. Finds the subtitles of a chosen title, picks useful phrases for the learner level (beginner, intermediate or advanced), pairs each phrase with a translation and its exact timestamp, and saves a study sheet with context lines, usage notes and a 10-question self-quiz after confirmation. Can give the timestamp to replay a phrase and, after confirmation, tag the video as studied. Use when the user says things like "make a Spanish lesson from Charade", "teach me French phrases from this film", "turn season 1 episode 3 into a Japanese study sheet", or "which useful English lines are in this movie".
---

# Subtitle Tutor

Subtitle Tutor turns a film or series the user already owns on the NAS into a language lesson. It reads the subtitles, chooses the phrases most worth learning at the user's level, and pairs each phrase with a translation and the exact moment it is spoken. It then writes a study sheet next to the user's other notes. All reading, translating and saving is done by the NAS experts listed below.

# Goal

The user receives one Markdown study sheet for one title, in one target language and at one level. The sheet contains:

- the requested number of phrases (default 20), each with:
  - a translation into the user's language
  - the start timestamp
  - the line spoken before and the line spoken after
  - a short usage note
- a 10-question self-quiz with an answer key.

The sheet is saved only after the user confirms, in `Language Lessons/{TITLE_SAFE}/` inside the user's personal folder or in another folder the user names.

Scope:

- Only video files and subtitle files that are already on the NAS, plus subtitles downloaded with explicit confirmation.
- Only external subtitle files in SubRip (`.srt`) or Advanced SubStation (`.ass`, `.ssa`) format. Subtitle tracks embedded inside a video container are out of scope.
- The Skill never deletes or moves files, never shares anything outside the NAS, and never changes the video file itself.

# Required input

Ask for any missing required item in one short message. Do not ask for anything else.

| Input | Required | Default and rules |
|---|---|---|
| Title of the film or series | yes | Free text, as the user calls it. |
| Season and episode | only for a series | Ask after step 2 if the match is a series and they were not given. |
| Target language (the language to learn) | yes | Language name; the Skill also records its ISO 639-1 code, for example Spanish = `es`. |
| User language (for translations and notes) | yes | If not stated, use the language of the user's message and say so in the summary. |
| Level | no | `beginner`, `intermediate` or `advanced`; default `intermediate`. |
| Number of phrases | no | Default 20; allowed 5 to 40. Values outside the range are set to the nearest limit and the user is told. |
| Scene range | no | A start and end time such as 00:20:00 to 00:45:00, or "first 30 minutes". Default: the whole title. |
| Destination folder | no | Default: `Language Lessons/{TITLE_SAFE}` inside the user's personal folder. |

Before step 2, repeat the inputs back in one line, for example: "Spanish phrases from Charade, intermediate, 20 phrases, whole film, translations into English". Then continue without waiting, unless something is missing.

# Runtime values

The values below are filled while the Skill runs. They are not placeholders for the author. Each one gets the real value from the step named in the table before any instruction that uses it is sent.

Rules for assembling instructions:

- If a value is still unknown, do not send the instruction. Stop at that step and report what is missing.
- When a filled value contains a single quote, write it as `'"'"'` so the instruction stays one single-quoted string.

| Value | Filled from |
|---|---|
| `{TITLE}` | User input. After step 2, the exact title returned by the media search. |
| `{TITLE_SAFE}` | `{TITLE}` with each slash, backslash, colon, asterisk, question mark, double quote, angle bracket and vertical bar replaced by `-`. |
| `{SEASON}`, `{EPISODE}` | User input (series only). `0` and `0` for a movie. |
| `{TARGET_LANG}`, `{TARGET_CODE}` | User input. |
| `{USER_LANG}`, `{USER_CODE}` | User input, or the language of the user's message. |
| `{LEVEL}`, `{COUNT}`, `{RANGE}` | User input or defaults. |
| `{MEDIA_ID}` | Step 2: media ID returned by `media-agent`. |
| `{VIDEO_PATH}` | Step 2: real file path returned by `media-agent` or `file-agent`. |
| `{VIDEO_DIR}` | The folder part of `{VIDEO_PATH}`. |
| `{USER_FOLDER}` | Step 2: folder path the user typed, used only when the media search returned no file path. |
| `{HOME_DIR}` | Step 4: real personal folder path returned by `file-agent`. |
| `{LESSON_DIR}` | `{HOME_DIR}` joined with `Language Lessons/{TITLE_SAFE}`, or the folder the user named. |
| `{SUB_PATH}` | Step 3: real path of one subtitle file returned by `file-agent`. |
| `{TARGET_SUB}`, `{USER_SUB}` | Step 3: subtitle file chosen for each language. |
| `{LANG_NAME}`, `{LANG_CODE}` | The language being searched for in step 3. |
| `{SUB_FILE_ID}` | Step 3: `file-id` of the candidate the user picked from the online subtitle search. |
| `{DOWNLOADED_PATH}` | Step 3: saved path, if `media-agent` reported one after the download. |
| `{OLD_SHEET_PATH}` | Step 4: real path of an earlier study sheet in `{LESSON_DIR}`. |
| `{LINES}` | Step 6: numbered phrases that still need a translation. |
| `{SHEET_NAME}` | Step 7: `{TITLE_SAFE} - {TARGET_LANG} {LEVEL} - YYYY-MM-DD.md`. Add ` (2)`, ` (3)` and so on if that name already exists. |
| `{SHEET_TEXT}` | Step 7: the finished sheet. |
| `{TAG_NAME}` | Step 9: `studied: {TARGET_LANG} {LEVEL}`. |

# Workflow

The Skill hands every NAS operation to a registered expert with a standard delegate command and never runs NAS commands itself. Each step uses only the real result returned by the expert in an earlier step, never a guessed path, ID or text. Steps 5 and 6 (choosing and pairing phrases) and the writing of the sheet are reasoning over that real result and do not touch NAS data.

| Step | Expert | Catalog capability the expert is expected to use |
|---|---|---|
| 2 Find the title | `media-agent`, `file-agent` | `ug-video` `search`; `ug-filesystem` `find` |
| 3 Find or download subtitles | `file-agent`, `media-agent` | `ug-filesystem` `ls`, `stat`, `cat`; `ug-filemgr` `tag-get-file`; `ug-video` `subtitle-search`, `subtitle-download` |
| 4 Read subtitles and earlier sheets | `file-agent` | `file-workflow` `get-user-dir`; `ug-filesystem` `ls`, `cat` |
| 6 Translate unmatched phrases | `document-agent` | `ug-document` `translate` |
| 7 Save the sheet | `file-agent`, `knowledge-agent` | `ug-filesystem` `stat`, `mkdir`; `ug-knowledge` `save-text` |
| 8 Replay | `media-agent` | `ug-video` `search` (play) |
| 9 Tag the video | `file-agent` | `ug-filemgr` `tag-get-by-name`, `tag-add`, `tag-add-file` |

## Step 1: Collect input

Collect the inputs described in Required input and repeat them back in one line.

## Step 2: Find the title (read only)

1. Send:

   `delegate --target media-agent --instruction 'Search the NAS video library for movies and TV series whose title matches {TITLE}. Read only: do not start playback and do not change anything. For every match return the exact title, the year, whether it is a movie or a series, the media ID, and the real file path of the video file. If there are no results, return an empty list and say so. Do not return similar or unrelated titles as matches.'`

2. Count a returned item as a match only if its title equals or contains {TITLE}, ignoring case and punctuation. If every returned title is clearly different, treat the result as no results. Then act on the result:
   - **No results:** tell the user "I could not find a title matching {TITLE} in the NAS media library." Stop. Do not offer other titles. The user may ask again with another title.
   - **One match:** use it.
   - **Several matches:** list them (title, year, movie or series, folder) and ask the user to choose one. This is `waiting_user`; continue only with the chosen item.
3. If the chosen match is a series, get `{SEASON}` and `{EPISODE}` from the user if they are missing, then send:

   `delegate --target media-agent --instruction 'For the TV series with media ID {MEDIA_ID} ({TITLE}), return the real file path of season {SEASON} episode {EPISODE}. Read only. If that episode is not in the library, say so and return no path. Do not return a different episode.'`

   If no path comes back, tell the user that episode is not in the library and stop.
4. If the media search returned the title but no real file path, ask the user which NAS folder holds the video file and record the answer as `{USER_FOLDER}`. Then send:

   `delegate --target file-agent --instruction 'In the folder {USER_FOLDER} and its subfolders up to two levels deep, find video files whose file name contains {TITLE}, ignoring upper and lower case. Read only. Return the real path, size and modification time of each match. If there are no results, return an empty list and say so.'`

   - **No results:** say that no video file for {TITLE} was found in that folder, and stop.
   - **Several matches:** ask the user to choose one.
5. Record `{MEDIA_ID}`, `{VIDEO_PATH}` and `{VIDEO_DIR}`.

## Step 3: Find the subtitles (read only unless the user confirms a download)

1. Send:

   `delegate --target file-agent --instruction 'List the files directly inside the folder {VIDEO_DIR}, without going into subfolders. Read only. Return the name, real path, size and modification time of every file whose name ends in .srt, .ass or .ssa, in upper or lower case. Also return the tags currently attached to the video file {VIDEO_PATH}. If the folder has no subtitle files, return an empty list and say so.'`

   Keep this list. It is the before-download snapshot used in item 5.

2. Work out the language of each subtitle file:
   - First use a language tag in the file name, for example `.en.`, `.eng.`, `.es.`, `.spa.`, `.ja.`, `.jpn.`, `English` or `Español`.
   - If the name has no tag, set `{SUB_PATH}` to that file's path and send:

     `delegate --target file-agent --instruction 'Read the first 3000 bytes of the text file {SUB_PATH} and return them exactly as stored, without summarising or changing anything. Read only.'`

     Identify the language from the returned text.
   - If two files have the same language, prefer the one whose base name matches the video file name. Otherwise ask the user to choose.
   - Record `{TARGET_SUB}` and `{USER_SUB}`.

3. If the tags returned in item 1 include `studied: {TARGET_LANG} {LEVEL}`, tell the user that this title was already studied at this level. Step 4 offers new phrases.

4. If a subtitle file is missing for the target language, the user language, or both:
   - Tell the user exactly which language is missing.
   - Ask: "Shall I search for {LANG_NAME} subtitles online? This uses the NAS video service to contact an online subtitle source outside the NAS. The film's details are sent to that source, and a subtitle file is downloaded into the video folder. Nothing else is sent."
   - Ask once per missing language. Continue only on a clear yes.
   - **If the user declines:**
     - Target-language subtitles missing: say a lesson cannot be built without them, and stop.
     - User-language subtitles missing: continue. Step 6 then uses the translation capability.

5. For each missing language the user approved:

   a. Set `{LANG_NAME}` and `{LANG_CODE}`, then send:

      `delegate --target media-agent --instruction 'Search online subtitles for the video {VIDEO_PATH} in {LANG_NAME} ({LANG_CODE}). Use season {SEASON} and episode {EPISODE}; both are 0 for a movie. Search only: do not download anything. Return up to 10 candidates with their file-id, file name, language, format and release or version name. If there are no results in this language, return an empty list and say so. Do not return other languages.'`

   b. **No results:** say "No {LANG_NAME} subtitles were found online for {TITLE}." Then apply the decline rule from item 4.

   c. **Candidates found:**
      - Show at most five, putting first those whose release name matches the video file name. A matching release lowers the risk of misaligned timings.
      - Ask the user to pick one and to confirm the download. This is `waiting_user`.
      - Record the chosen `file-id` as `{SUB_FILE_ID}`.

   d. Only after the user confirms, send:

      `delegate --target media-agent --instruction 'Download the subtitle with file-id {SUB_FILE_ID} for the video {VIDEO_PATH}. The user has confirmed this download from an online source outside the NAS. Download only this one file. Do not change, move or remove any other file. Return the download status and, if known, the saved file path.'`

      The NAS may show its own approval prompt for this download. This is `waiting_approval`.

   e. After `completed`, send:

      `delegate --target file-agent --instruction 'List the files directly inside the folder {VIDEO_DIR} again, without going into subfolders. Read only. Return the name, real path, size and modification time of every file whose name ends in .srt, .ass or .ssa, in upper or lower case. If there are no results, return an empty list and say so.'`

      The downloaded file is a path that is in this list but not in the snapshot from item 1.

   f. If that comparison finds nothing, but the download reported a saved path, record it as `{DOWNLOADED_PATH}` and send:

      `delegate --target file-agent --instruction 'Check whether the file {DOWNLOADED_PATH} exists. Read only. Return its real path, size and modification time, or say that it does not exist.'`

   g. Decide:
      - **Exactly one new subtitle file confirmed:** use it.
      - **None:** say "The download was reported, but no new subtitle file could be found." Apply the decline rule from item 4.
      - **Several:** ask the user which one to use.

## Step 4: Read the subtitles and any earlier sheet (read only)

1. Set `{SUB_PATH}` to `{TARGET_SUB}` and send the instruction below. Then do the same for `{USER_SUB}`, if it exists.

   `delegate --target file-agent --instruction 'Read the whole text file {SUB_PATH} and return its content exactly as stored, without summarising, translating or removing lines. Read it in consecutive chunks of 65536 bytes starting at offset 0 until the end of the file. Return the chunks in order, with the total size in bytes. Read only. If a chunk cannot be read, return the chunks already read and say at which offset reading stopped.'`

2. Parse the returned text into cues with start time, end time and text, following [references/phrase-selection.md](references/phrase-selection.md). Keep only cues whose start time is inside `{RANGE}`.
   - If the target file gives zero cues, or the text is unreadable (for example wrong encoding), say so and stop. Do not guess the content.
   - If reading stopped part-way:
     - Tell the user which time span was read.
     - Ask whether to continue with that span or stop.
3. Find the destination and any earlier sheet. Send:

   `delegate --target file-agent --instruction 'Return the real path of the personal folder of the current user. Read only. Do not create or change anything.'`

   Record `{HOME_DIR}` and set `{LESSON_DIR}`, unless the user named another folder. Then send:

   `delegate --target file-agent --instruction 'Check whether the folder {LESSON_DIR} exists. If it exists, list the files directly inside it with name, real path and modification time. Read only. Do not create or change anything. If the folder does not exist or is empty, say so.'`

4. If an earlier sheet for the same title, language and level exists, offer to choose new phrases that are not in it. On yes, set `{OLD_SHEET_PATH}` and send:

   `delegate --target file-agent --instruction 'Read the text file {OLD_SHEET_PATH} and return its content exactly as stored, without summarising or changing anything. Read only.'`

   Phrases already in it are excluded in step 5.

## Step 5: Choose the phrases (reasoning over the real subtitle text)

Select `{COUNT}` phrases from the target-language cues, using the rules in [references/phrase-selection.md](references/phrase-selection.md):

- level fit
- everyday usefulness
- frequency in this title
- spread across the scene range

Never select:

- names or places on their own
- one-word fillers
- sound descriptions
- song lyrics
- subtitle credits or advertising lines
- slurs.

Keep the excerpts short: at most 12 words per phrase and at most 15 words per context line.

If fewer suitable phrases exist than requested, select all of them and tell the user the real number. This is a partial result.

## Step 6: Pair each phrase with a translation

1. If `{USER_SUB}` exists, run the alignment check in [references/phrase-selection.md](references/phrase-selection.md) first. It has three outcomes:
   - **Aligned:** pair each phrase with the user-language cue at the same timestamp, marked "subtitle".
   - **Constant offset:** shift the user-language cues by the measured offset, tell the user the offset in seconds, and pair as above.
   - **Misaligned:** the two files come from different versions, cuts or frame rates. Tell the user, and do not pair by timestamp. Offer three choices:
     - translate the phrases with the NAS translation capability;
     - choose or download another user-language subtitle (back to step 3);
     - stop.
2. Phrases still without a translation go into `{LINES}` as numbered lines. Send them, at most 40 lines per instruction:

   `delegate --target document-agent --instruction 'Translate the following numbered lines from {TARGET_LANG} ({TARGET_CODE}) into {USER_LANG} ({USER_CODE}). Translate the given text only: there is no source file. Do not save an output file. Return the translation of each line with its number, in the same order, and nothing else. If this language pair is not supported, say so and return failed instead of guessing. Lines: {LINES}'`

   The NAS may ask for approval for translation. This is `waiting_approval`. Mark these translations "machine translation".

3. If translation returns `failed` because the pair is not supported:
   - Tell the user: "The NAS translation capability does not support {TARGET_LANG} to {USER_LANG}." Never invent a translation.
   - Offer two choices:
     - save the sheet with those phrases marked "no translation available";
     - stop.
4. If the translation expert reports an `output_file`, tell the user its path.

## Step 7: Write the study sheet and save it after confirmation

1. Write `{SHEET_TEXT}` exactly in the format of [references/study-sheet-format.md](references/study-sheet-format.md). It includes the phrases, the 10-question self-quiz with answer key, the source subtitle files, the alignment result and any flags.
2. Pick `{SHEET_NAME}` so that it does not match a file listed in step 4.
3. Show the user:
   - the number of phrases;
   - the first three phrases as a preview;
   - the full destination `{LESSON_DIR}/{SHEET_NAME}`;
   - whether the folder will be created.

   Ask: "Save the study sheet here?" This is `waiting_user`.
   - **No:** show the sheet in the conversation instead and stop. Nothing is written.
   - **A different folder:** use the folder the user names, and repeat step 4 item 3 for it.
4. If `{LESSON_DIR}` does not exist, send:

   `delegate --target file-agent --instruction 'Create the folder {LESSON_DIR}, including missing parent folders. The user has confirmed this. Do not change, move or remove anything else. Return the real path of the created folder.'`

5. Check for a name clash just before saving. Send:

   `delegate --target file-agent --instruction 'Check whether a file named {SHEET_NAME} exists in the folder {LESSON_DIR}. Read only. Return yes or no and, if yes, its real path and modification time.'`

   If it exists, ask the user to choose:
   - a new name (recommended; adds ` (2)`);
   - replace the existing file;
   - cancel.

   Replace it only after an explicit "replace".
6. Send one of these:
   - **New file (normal case):**

     `delegate --target knowledge-agent --instruction 'Save the following Markdown text as a new file named {SHEET_NAME} in the folder {LESSON_DIR}. The user has confirmed this save. Do not replace an existing file, and do not change any other file. Return the real output file path, the byte count and whether the save was verified. Text: {SHEET_TEXT}'`

   - **Replace (only after the user explicitly chose "replace" in item 5):**

     `delegate --target knowledge-agent --instruction 'Save the following Markdown text as the file {SHEET_NAME} in the folder {LESSON_DIR}, replacing the existing file of the same name. The user has explicitly confirmed replacing it. Do not change any other file. Return the real output file path, the byte count and whether the save was verified. Text: {SHEET_TEXT}'`

   The NAS may ask for approval for the save. This is `waiting_approval`.
7. Report the save as done only when the result is `completed` with a verified save and a real output path. Give the user that path.

## Step 8: Replay a phrase (optional, on request)

When the user asks to replay a phrase (for example "replay phrase 7"):

1. Give its timestamp minus two seconds, as a lead-in, together with the line before and the line after.
2. Explain that the NAS video controls in this Skill cannot jump to a time. The user seeks to that time in the player.
3. Offer to start the title. On yes, send:

   `delegate --target media-agent --instruction 'Start playback of the video with media ID {MEDIA_ID} ({TITLE}) in the NAS video player. The user asked for this. Do not change anything else. Return whether playback started and on which player.'`

   If playback does not start, say so and give the timestamp only.

## Step 9: Tag the video as studied (optional, after confirmation)

1. Ask: "Tag the video file with {TAG_NAME} so you can see later that you studied it?" Continue only on yes.
2. Send:

   `delegate --target file-agent --instruction 'Attach the tag named {TAG_NAME} to the video file {VIDEO_PATH}. The user has confirmed this. First look up an existing tag with exactly this name, and create the tag only if none exists. Do not remove or change any other tag or file. Return the tag ID and whether the tag is now attached to the file.'`

   The NAS may ask for approval. This is `waiting_approval`.
3. If the tag name is rejected, report the exact reason. Offer `studied-{TARGET_CODE}-{LEVEL}` as an alternative name, and use it only after the user agrees.

# Completion and failure

## Delegation states

Every delegation ends in one of five public states. Handle each one explicitly:

| State | What the Skill does |
|---|---|
| `completed` | Use only the real result data. Check that the fields the next step needs are present, for example a real path or a `file-id`. If a needed field is missing, treat the step as `failed`. |
| `failed` | Tell the user in plain words which step failed and the reason the expert gave. Stop every step that depends on it. Keep and report the results already obtained. Do not retry with guessed values. |
| `cancelled` | Say what was cancelled and what was not done. For example: "Nothing was downloaded." "The sheet was not saved." Stop that branch. |
| `waiting_user` | Pass the expert's question to the user unchanged, wait for the answer, and send it back. Do not answer for the user. |
| `waiting_approval` | Tell the user what is waiting for approval: a download from outside the NAS, a new folder, a save, a translation or a tag. Wait for the approval result. If approval is refused, treat the step as `cancelled`. |

## Failure catalogue

| Situation | Message and behaviour |
|---|---|
| Title not found | "No title matching {TITLE} is in the NAS media library." Stop. No similar titles are offered as substitutes. |
| Series episode not found | Say which episode is missing. Stop. |
| No subtitles at all | Local files and online search both gave no results, or the user declined the download. Say so and stop. Embedded subtitle tracks are not used. |
| Target-language subtitles missing | A lesson cannot be built. Stop after saying which language is missing. |
| User-language subtitles missing | Continue with the NAS translation capability. Mark every translation "machine translation". |
| Unsupported language pair | Say the pair is not supported. Offer to save without translations (clearly marked) or stop. Never guess. |
| Misaligned subtitle versions | Name the measured problem (offset, drift or cue-count gap). Offer translation, another subtitle file, or stop. |
| Unreadable or empty subtitle file | Name the file and the problem. Stop if it is the target-language file. |
| Partial read | Report the time span that was read. Ask whether to continue with it. |
| Fewer phrases than requested | Deliver the real number and say so. |
| Folder creation or save failed | Report the reason. Show the sheet in the conversation so no work is lost. Do not write it elsewhere without asking. |
| Tag failed | Report the reason. The saved sheet is not affected. |
| Playback not available | Give the timestamp only. |

## Final report

At the end, give a short report:

- the title and the subtitle files used;
- the number of phrases, and how many were translated by subtitle and how many by machine;
- the alignment result;
- the saved file path, only if the save was verified;
- whether the tag was added;
- anything that was skipped or failed.

# Privacy and data flow

- **Stays on the NAS:**
  - the video files;
  - the subtitle text;
  - the study sheet;
  - the tags.

  The Skill reads only:
  - the chosen video folder;
  - a folder the user names to locate the video, if the media library gave no file path;
  - the destination folder and the earlier sheets in it.
- **The only outside connection is the optional subtitle search and download.** It goes through the NAS video service, and only after the user's explicit yes. The user is told beforehand that it contacts an online subtitle source outside the NAS.
- **Nothing is shared or sent anywhere else.** The Skill has no sharing step.
- **The sheet is for personal study.** It keeps only short excerpts of the subtitles:
  - at most 12 words per phrase;
  - at most 15 words per context line.
- **No account data, passwords or keys** are requested or stored.

# Generation-time capability evidence

Catalog: `uliya-skill-kit` 0.7.3, `data/capability-catalog.json`, version 2.0.0. Each CLI has one owning expert:

- `ug-video` → `media-agent`
- `ug-filesystem` → `file-agent`
- `ug-filemgr` → `file-agent`
- `file-workflow` → `file-agent`
- `ug-document` → `document-agent`
- `ug-knowledge` → `knowledge-agent`

Not available in the catalog, and therefore not claimed:

- seeking a video to a timestamp: `ug-video` `control` offers only pause, continue, next and previous;
- a published list of translation language pairs;
- reading subtitle tracks embedded inside a video file.

# References

- [references/phrase-selection.md](references/phrase-selection.md): subtitle parsing, phrase selection by level, and the alignment check.
- [references/study-sheet-format.md](references/study-sheet-format.md): sheet layout, file name, usage notes and self-quiz rules.
- [references/disclosures.md](references/disclosures.md): third-party components and licences, functionality built for the UGREEN Hackathon 2026, and AI tools used.
