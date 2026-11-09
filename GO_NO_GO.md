# Subtitle Tutor: go/no-go (Step 0)

Date: 2026-11-09
Source of truth: UGOS Skill Creation Tool `uliya-skill-kit` 0.7.3 (English build), file `data/capability-catalog.json`, `catalogVersion` 2.0.0, `generatedAt` 2026-09-01.
Method: the kit's own capability-query flow ("Do not generate any files yet. Help me check whether this idea is currently supported and suitable as a UGREEN NAS skill"), reading every CLI, Action, parameter, effect and approval value in the catalog. No Skill files were generated for this step.

> Caveat about the catalog itself: in the English build, the Chinese parts of many free-text fields were removed during translation. Examples: `returnSummary` for `ug-video search` reads "Media、、、PlayPlayresult；PlayRequiresreal ID/path", and `permissions`, `prerequisites`, `errorCodes` and `stability` are `"unknown"` for every Action. CLI names, Action names, parameters, enums, `effect` and `approval` are intact. The answers below rely only on those intact fields. Where a fact depends on a removed text field, it is marked **not stated in catalog**.

## Verdict: GO

Questions 2 and 3 are both supported. Question 3 is supported through the **file** expert (`ug-filesystem` → `cat`), not through the document expert. Three gaps need design workarounds, and none of them blocks the idea:

| Gap | Workaround in the Skill |
|---|---|
| Where `subtitle-download` saves the file is not stated in the catalog | List the video folder before and after the download and report the new file actually found. If no new file appears, say so and stop. |
| Translation language pairs are not listed in the catalog | Prefer the second-language subtitle line at the same timestamp. Call `translate` only for gaps. If `translate` fails, report the pair as unsupported and do not guess. |
| No video seek action | Give the exact timestamp to jump to. Only offer playback without a start position. |

## Capability → expert mapping used below

| CLI | Agent (single owner, from catalog) |
|---|---|
| `ug-video` | `media-agent` |
| `ug-filesystem` | `file-agent` |
| `ug-filemgr` | `file-agent` |
| `ug-document` | `document-agent` |
| `ug-knowledge` | `knowledge-agent` |

The parent Skill may only `delegate --target <agent> --instruction '<task>'`. The expert picks and runs the CLI/Action itself.

---

## 1. Can the Skill find a video in the media library by title?

**Yes.**

- `ug-video` → `search` (`media-agent`). `effect=mixed`, `approval=none`. Relevant parameters: `type` (required; use `media`), `keyword` (the title), `classification` (`all|movie|tv|other`), `video-type` (`all|movie|tv|collection`), `episode`, `limit`, `page`. Catalog example: `--type media --keyword "流浪地球"`.
- The returned fields are **not stated in catalog** (the `returnSummary` text was stripped). The surviving words say playback needs a "real ID/path". That suggests the result carries an ID and/or path, but this is unconfirmed.
- Backup route to a real file path: `ug-filesystem` → `find` (`file-agent`, `effect=read`, `approval=none`). Parameters are `path` (required root), `pattern`, `type` (includes `video`), `max-depth` and `limit`. It returns real paths with `fileId`.
- Several matches: the Skill lists them and asks the user to choose. No match: the Skill says so and stops.

## 2. Can it find subtitle files next to a video? Can the video expert download subtitles for a chosen language, and where is the file saved?

**Subtitle files next to the video: yes.**

- `ug-filesystem` → `ls` (`file-agent`, `read`, `approval=none`). Parameters: `path` (required), `recursive`, `max-depth`, `limit`. Returns entries with real paths and `fileId`.
- `ug-filesystem` → `find` (`file-agent`, `read`, `approval=none`) on the video's own folder, with `pattern` such as `*.srt` / `*.ass`, `type=file` and `max-depth=1`.
- Both need the real video path returned by question 1.

**Download for a chosen language: yes, as two Actions.**

1. `ug-video` → `subtitle-search` (`media-agent`, `effect=read`, `approval=none`). Parameters: `video-path`, `query`, `season-number` (default 0), `episode-number` (default 0). Returns subtitle candidates with a `file-id`. There is **no dedicated language parameter**. The language goes into `query` as text; the catalog example is `--query "中文字幕"` ("Chinese subtitles").
2. `ug-video` → `subtitle-download` (`media-agent`, `effect=state-change`, `approval=gateway`). Parameters: `video-path` (required) and `file-id` (required). Returns a download `status`.
- Catalog boundary for this scenario: the download must use a real `file-id` returned by `subtitle-search`. It must never use a media/search ID.

**Where the file is saved: not stated in catalog.** The Action takes the video path, so the file is likely saved alongside that video, but the catalog does not give the destination folder or file name. The Skill therefore:

1. lists the video folder with `ug-filesystem` → `ls` before the download,
2. lists it again after `subtitle-download` returns `completed`,
3. uses only a new `.srt`/`.ass` file that it actually found. If none is found, it reports that and stops.

**External data flow:** the online subtitle source behind `subtitle-download` is not named in the catalog. The Skill must tell the user that this fetches a file from outside the NAS and get confirmation first. The `approval=gateway` value also means the platform will ask for approval.

## 3. Can the document expert read the text of a subtitle file (.srt/.ass) with timestamps?

**Document expert: not confirmed. File expert: yes.**

- `ug-document` → `qa` (`document-agent`, `read`). It supports `intent=content_read` and `content-scope=full`, and returns `answer`, evidence and coverage. `ug-document` → `extract` and → `metadata` also read documents. However, the catalog **does not list the file formats** `ug-document` accepts, and nothing confirms `.srt`/`.ass`. It also returns an answer rather than verbatim text, so timestamp fidelity is not guaranteed.
- `ug-filesystem` → `cat` (`file-agent`, `effect=read`, `approval=none`). Parameters: `path` (required), `offset`, `length`. It returns file content. `.srt` and `.ass` are plain-text formats, so cue numbers, `00:41:12,480 --> 00:41:15,020` timing lines and `.ass` `Dialogue:` lines come back verbatim. `offset`/`length` allow chunked reading of a long film. The optional scene range keeps the volume down.
- **Decision:** step 4 of the Skill uses `ug-filesystem` → `cat` through `file-agent`.
- Out of scope: subtitle tracks embedded inside the video container (for example MKV). No catalog Action extracts them. If only embedded tracks exist, the Skill reports "no external subtitle file" and offers the download route.

## 4. Which translation language pairs are supported?

**Not listed in the catalog.**

- `ug-document` → `translate` (`document-agent`, `effect=mixed`, `approval=gateway`). Parameters: `query`, `file`, `target-lang`, `style`, `body-cap`, `max-files` (default 5), `extract-only` (default false), `content`, `source-title`. Returns `mode`, `translation`, `output_file`, `target_lang`, coverage, sources and safety.
- `target-lang` is a free string (example `en`). There is **no source-language parameter and no enum of languages**, so no pair can be promised before testing on a NAS.
- `content` accepts inline text, so phrases can be translated without a source file. Because `effect=mixed` and `output_file` exists, the expert may also write a file. The Skill asks for the translation text only, and reports any `output_file` it is told about.
- **Design consequence:** the primary pairing comes from the user's-language subtitle at the same timestamp, which needs no translation call. `translate` covers only lines without a match. A `failed` result is reported as "this language pair could not be translated" and is never guessed.

## 5. Can it save a text document to a chosen folder, and tag a file?

**Save: yes.**

- `ug-knowledge` → `save-text` (`knowledge-agent`, `effect=state-change`, `approval=workflow`). Parameters: `path`, `content`, `content-ref`, `filename-hint`. Returns `verified=true`, `outputFile`, `contentBytes`.
- Folder creation: `ug-filesystem` → `mkdir` (`file-agent`, `state-change`, `approval=gateway`). Parameters: `path` (required), `mode`, `parents`.
- Existence check before writing: `ug-filesystem` → `stat` / → `ls` (`file-agent`, `read`). Whether `save-text` overwrites an existing file is **not stated in catalog**, so the Skill checks first and asks before any overwrite.

**Tag: yes.**

- `ug-filemgr` → `tag-list` and → `tag-get-by-name` (`file-agent`, `read`): find an existing tag.
- `ug-filemgr` → `tag-add` (`file-agent`, `state-change`, `approval=gateway`; parameters `tag-id` (required), `colour`): create the tag if it is missing.
- `ug-filemgr` → `tag-add-file` (`file-agent`, `state-change`, `approval=conditional`; parameters `path` (required), `tag-id` (required)): attach the tag to the video file.

## 6. Optional: can playback start at a specific timestamp?

**No.**

- `ug-video` → `control` (`media-agent`, `state-change`, `approval=none`) accepts only `operation` = `pause|continue|next|previous`. It has no seek and no position.
- `ug-video` → `search` has a `play` parameter (`effect=mixed`) that can start a found title. It has **no start-position parameter**.
- `ug-music` → `control` does have `seek` with `position-ms`, but it belongs to the music domain and cannot be applied to video. It is not used.
- **Design consequence:** "replay this phrase" gives the exact timestamp (for example "jump to 00:41:12") and the lines around it. As an optional extra, the Skill can start the title through `ug-video` → `search` with `play` and tell the user where to seek. Whether `play` works and where it plays is a finalist-day validation item.

---

## Capabilities considered and deliberately not used

- `ug-knowledge` → `audio-transcription`: the catalog shows audio paths only. Its use on a video file is unconfirmed, so it is not offered as a "no subtitles" fallback.
- `ug-filemgr` → `mediainfo`: it might list embedded subtitle streams, but its returned fields are not stated in the catalog. It is not needed for the core flow.
- `ug-filesystem` → `echo` / → `touch`: they could write the sheet, but `ug-knowledge` → `save-text` returns verification (`verified=true`, `outputFile`), so it is used instead.

## Track

**Open Innovation** (confirmed against the track definitions on the Devpost overview and rules). It "combine[s] the NAS, AI, media, file and knowledge capabilities provided for the challenge to build an original AI Skill that solves a real user need". The Skill chains media (`ug-video`), file (`ug-filesystem`, `ug-filemgr`), document (`ug-document` translate) and knowledge (`ug-knowledge` save) capabilities.

The other tracks fit less well:

- Automate Your Workflow covers office-style organising and extraction.
- Bring Memories to Life covers personal photos and videos.
- Unleash Your Creativity is aimed at content creators.

## Items to validate on a real NAS (finalist day)

1. `ug-video` → `search` result fields: is the on-disk path included? If not, use the `ug-filesystem` → `find` route.
2. `subtitle-search` → `subtitle-download`: language matching via `query`, plus the save location and file name.
3. `ug-filesystem` → `cat` on a 100 KB `.srt`: chunk size and UTF-8 handling.
4. `ug-document` → `translate` with inline `content`: which `target-lang` values work, and whether `output_file` is written.
5. `ug-knowledge` → `save-text` into a new subfolder: behaviour when the file name already exists.
6. `ug-filemgr` → `tag-add-file` on a video file: `approval=conditional` behaviour.
7. `ug-video` → `search` with `play`: whether and where playback starts.
