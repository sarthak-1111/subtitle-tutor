# Compliance checklist: Subtitle Tutor

Sources read on 2026-11-09:

- **[DP]** Devpost overview: https://ugreenhackathon.devpost.com
- **[R]** Official Rules: https://ugreenhackathon.devpost.com/rules
- **[SK]** Hackathon Starter Kit: https://ai.ugreen.com/pages/hackathon-starter-kit
- **[AS]** UGREEN SkillHub Content Submission and Publication Standards (linked from [SK])
- **[KIT]** UGOS Skill Creation Tool `uliya-skill-kit` 0.7.3: its `SKILL.md`, `references/*.md`, `docs/skill-development-standard.md`, `data/capability-catalog.json` and the static checker `scripts/check-lib.mjs`. The checker is the concrete form of the standard.

Status key: `[x]` done and verified · `[ ]` open.

**Status as of 2026-11-09, after Step 2:**

- Sections B–G are verified against the built files:
  - `subtitle-tutor/` passes the official checker with `static-pass`, 0 errors and 0 warnings (see CHECK_RESULT.md);
  - the copy extracted from `dist/subtitle-tutor.zip` gives the same result;
  - the proposal's ten answers total 409 words, and the whole PDF 484 words.
- Sections A, H and I list actions for the entrant (eligibility, Devpost upload, Submit) or for the finalist day.

## A. Deadlines and eligibility

- [ ] Round 1 deadline: **Nov 15, 2026, 11:45 pm PT = Nov 16, 16:45 JST** [R §1]. Internal target: Nov 16, 12:00 JST.
- [ ] Entrant lives in an eligible country (Japan is on the Asia-Pacific list) and is of legal age [R §3].
- [ ] One project per entrant [R §4 "Multiple Submissions"].
- [x] All submitted materials in English [R "Language Requirements"].
- [ ] Round 1 materials stay in place after submission. Do not delete them [DP, R §5].

## B. Skill package (ZIP): structure and limits

- [x] Built with the official UGOS Skill Creation Tool, which must be used [DP, R §4, SK].
- [x] Follows the Uliya Skill Development Standard [R, KIT].
- [x] `SKILL.md` is the single required entry point [R, KIT].
- [x] Optional supporting files are Markdown only, under `references/`, each **directly linked** from `SKILL.md` [R, KIT `skill-format.md`]. Unlinked references produce warning `RESOURCE_UNREFERENCED`.
- [x] The package root contains **only** `SKILL.md` and `references/`. The checker raises error `RESOURCE_UNSUPPORTED` for any other root item, **including README.md**. README.md is therefore **not** placed in the ZIP. The starter-kit page calls README "recommended", but the official checker and [R] ("Separate manifests, scripts, executables, binaries, and other unsupported files are prohibited") take precedence.
- [x] Folder name equals frontmatter `name` = `subtitle-tutor` (error `SKILL_NAME_MISMATCH`).
- [x] Frontmatter has only `name` and `description`, each a single line. `name` is lowercase and hyphenated, 2–64 characters. `description` is at most 1,024 characters [R, KIT].
- [x] `description` states the user trigger ("Use when …"), otherwise warning `DESCRIPTION_TRIGGER_MISSING`.
- [x] ZIP ≤ 10 MB, uncompressed ≤ 10 MB, ≤ 1 MB per file, ≤ 100 files [DP, KIT].
- [x] `SKILL.md` body ≤ 500 lines (recommendation, warning).
- [x] No manifests, sidecars, scripts, executables or binaries [DP, R, SK, KIT].
- [x] No runtime code fences (` ```bash/sh/python/js/ts `) anywhere (error `SECURITY_SCRIPT_EXECUTION_UNSUPPORTED`).
- [x] No password protection on the ZIP; no path traversal, absolute paths or symlinks [R, AS §5.1].
- [x] The kit itself is **not** included in the ZIP or in any repository. It is only installed locally in `~/.claude/skills/uliya-skill-kit` (licence terms of [R §4] and [SK]).

## C. Required SKILL.md content

- [x] Sections the checker recognises: `# Goal`, `# Required input`, `# Workflow` (or `# Orchestration`), `# Completion and failure`. The template heading `# Expert orchestration` does **not** match the checker's pattern, so `# Workflow` is used.
- [x] Section `# Generation-time capability evidence` with lines in the exact form `` - `cli` → `agent` `` (Unicode arrow →). One line per CLI, and each agent must match the catalog's single owner (errors `CAPABILITY_EVIDENCE_*`).
- [x] Every NAS step is a `delegate --target <agent-id> --instruction '<task>'` command [KIT]:
  - single-quoted instruction;
  - no other `--flag` inside the command, so CLI parameters are written in prose, never as `--param`;
  - no pipes, redirects (` | `, ` < `, ` > `) or backticks inside;
  - no `<…>` placeholders inside the instruction (warning `DELEGATE_DYNAMIC_VALUE_UNRESOLVED`).
- [x] Delegate targets are only registered experts. This Skill uses `media-agent`, `file-agent`, `document-agent` and `knowledge-agent`.
- [x] The parent never runs `cli.invoke` directly [KIT].
- [x] All five delegation states are handled by name: `completed`, `failed`, `cancelled`, `waiting_user`, `waiting_approval` [KIT].
- [x] Each step uses the **real result** of the previous step, with no vague "that folder from before" [SK, KIT]. Variables are defined once and filled only from verified expert results.
- [x] Empty-result handling is stated: if nothing is found, say so and stop, and never substitute similar content [SK, KIT].
- [x] Partial-result handling is stated [KIT].
- [x] Completion and failure handling is stated [R, KIT].

## D. Capabilities

- [x] Only capabilities present in `data/capability-catalog.json` (v2.0.0) are used; none is invented [SK, KIT, R §4]. See GO_NO_GO.md for the exact CLI/Action names.
- [x] Unsupported needs are stated as unsupported (video seek, a list of translation pairs, the documented save location for downloads) and are not implied [KIT `docs`].
- [x] No claim of NAS execution from local generation or static checks [KIT]. No on-device results are claimed before the finalist day.

## E. Safety, confirmation and privacy

- [x] The user confirms before deleting, moving, overwriting, downloading from outside, or sharing [SK, AS §4.6]. This Skill **never deletes or moves** anything. It asks before downloading, creating a folder, saving, overwriting and tagging.
- [x] The external subtitle download is disclosed as a data flow from outside the NAS, with explicit confirmation each time [AS §2.4, §6.1, R "Third Party Integrations"].
- [x] Nothing is sent or shared outside the NAS by the Skill. Study sheets keep short excerpts for personal use [AS §6.4, §11].
- [x] No credentials, keys, tokens or personal data [R, SK, AS §5.3, §7.1]. The checker's credential patterns must report nothing.
- [x] No download-and-execute and no shell-download wording (the checker flags the words for common download tools as `SECURITY_REMOTE_DOWNLOAD`).
- [x] No wording that bypasses or switches off approval, permission or audit (checker `SECURITY_GATEWAY_BYPASS`), and no instruction override [AS §2.7, §3].
- [x] No hard-coded NAS paths (` /nas/…`, ` /volume1/…`) and no hard-coded home directories (checker `SECURITY_DIRECT_FILE_ACCESS`, `DELEGATE_HARDCODED_HOME_PATH`). All paths come from expert results or from the user.
- [x] Least privilege: the Skill reads only the chosen video's folder and the chosen study folder [AS §4.1, §4.2].
- [x] No persistence, background jobs or schedules [AS §5.4].
- [x] Minors [AS §10.2]: the Skill is not directed at, or primarily intended for, minors. Users are adult learners and parents who prepare material for their family. The wording avoids targeting children directly.

## F. Honesty and originality

- [x] Name and description match the real workflow, with no superlatives and no "official/certified" claims, and the Skill is not presented as a UGREEN product [SK §8, AS §2.2, §2.3, §11.2].
- [x] No TODO, TBD, "replace-with-" or placeholder content (checker `SKILL_PLACEHOLDER_REMAINS`) [SK].
- [x] Original work, newly developed during the Hackathon. No reused Skill or submission material [R §4 "New & Existing Projects"].
- [x] Disclosures in SKILL.md or a linked reference [DP, R]:
  - third-party components and licences (expected: **none**);
  - main functionality developed for this Hackathon;
  - AI tools used and what for (Claude Code, drafting and checking the Skill text).
- [x] Copyright of film subtitles: the Skill quotes only short phrase excerpts for personal study. Demo media for finalist day is a public-domain film with subtitles we have the right to use [R "Final Demo Video", AS §11].

## G. Proposal PDF (Round 1)

- [x] Separate PDF, ≤ 1 MB [DP].
- [x] Answers **all ten** official items [DP, R §4]:
  1. one-sentence description;
  2. target user and problem;
  3. solution;
  4. core user flow;
  5. difference from existing tools;
  6. NAS capabilities by step;
  7. technical approach;
  8. development status;
  9. validation plan (two core cases and one edge case);
  10. known limits, risks and dependencies.

  Third-party components are listed separately.
- [x] The ten answers total ≤ 500 English words. Third-party licence information, names and signatures are excluded from the count [DP, R].
- [x] States plainly that nothing has run on a real NAS yet [R §6 "A lack of NAS runtime evidence will not … lower its Round 1 score"].

## H. Devpost form and judging

- [ ] Track selected: **Open Innovation** (see GO_NO_GO.md).
- [x] Judging criteria, equally weighted [R §6]:
  - User Value;
  - Innovation & Differentiation;
  - Technical Quality;
  - AI NAS Fit & Validation.

  devpost.md maps the text to these four official names. They correspond to the brief's "Usefulness", "Creativity", "Technical Execution" and "AI NAS Fit".
- [ ] Upload the PDF and the ZIP, then press Submit before the deadline.

## I. Finalist day (only if selected)

- [ ] Credentials go to the Representative and are valid for one assigned day between Nov 22 and Nov 28 [R §4].
- [ ] The NAS is used only to install, test and record this Skill [R].
- [ ] Logs and test data are backed up before the testing day ends [R "Testing"].
- [ ] Demo video under 3 minutes, English narration, public on YouTube, showing the Skill running on the assigned NAS. No third-party copyrighted material without permission, so the demo uses a public-domain film [R].
- [ ] Final ZIP submitted by Nov 30, 11:45 pm PT [R].
