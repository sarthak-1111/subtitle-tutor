# Check result: subtitle-tutor

- **Date:** 2026-11-09
- **Tool:** UGOS Skill Creation Tool `uliya-skill-kit` 0.7.3. The kit's "Help me check this skill" intent runs its bundled read-only checker, `scripts/check-skill.mjs`, with check format 2.0.0 and capability catalog 2.0.0.
- **Target:** the `subtitle-tutor/` folder exactly as packed in `dist/subtitle-tutor.zip`, unpacked from the ZIP before the check. It contains six files: `SKILL.md`, `references/disclosures.md`, `references/example-sheet.md`, `references/install-and-testing.md`, `references/phrase-selection.md` and `references/study-sheet-format.md`.
- **Command:** `node scripts/check-skill.mjs <unpacked ZIP>/subtitle-tutor`, run from the kit folder. The exit code was 0.

## Result: `static-pass`, with 0 errors, 0 warnings and 0 info

There are no required changes and no recommended changes.

The checker was run after every change to the Skill during development. One intermediate run of version 1.1.0 reported `RESOURCE_UNSUPPORTED`, because a reference file contained the Unicode replacement character itself as an example; the text now names it as "U+FFFD" instead. Every other run returned `static-pass`.

The SHA-256 values below identify the exact files in the ZIP (UTF-8, LF line endings). They match `sha256sum` of the unpacked files.

**Scope of a static pass:** the kit states that a static pass "does not prove upload, installation, compatibility, or device execution". Nothing has been run on a UGREEN NAS yet. Off-device stand-in tests on a PC are in [`testbed/RESULTS.md`](testbed/RESULTS.md); they are not NAS results. Validation on a device is planned for the finalist testing day; see [`FINALIST_DAY.md`](FINALIST_DAY.md).

## Raw checker output

```json
{
  "checkFormatVersion": "2.0.0",
  "status": "static-pass",
  "target": {
    "skillName": "subtitle-tutor"
  },
  "catalog": {
    "checkedVersion": "2.0.0"
  },
  "files": [
    {
      "path": "references/disclosures.md",
      "sha256": "f6cf75d3ee85675f6ba8ee81a2ab0c996990ec1012d58ffe9c3949295fe359f8"
    },
    {
      "path": "references/example-sheet.md",
      "sha256": "6ad322284c9885f1ae34e2240e7fb3537748157acd0f66c788b264692cb66ba9"
    },
    {
      "path": "references/install-and-testing.md",
      "sha256": "79ef3939a3a94ff4e9031adf99a008787d880d8eb4adcc1dffe07b58a8090d80"
    },
    {
      "path": "references/phrase-selection.md",
      "sha256": "89a86ec774d3a96148b6516442848369bd3201d1329e984127485f8f06655b60"
    },
    {
      "path": "references/study-sheet-format.md",
      "sha256": "15c178a6bda15558ffecd1057256f97ff430cf34aef8eae4be3e9450cb7cfd76"
    },
    {
      "path": "SKILL.md",
      "sha256": "10ae659352b81b648297da99ef9aadef050c2b7cc2e445e2d309e5e8d01a348b"
    }
  ],
  "summary": {
    "errors": 0,
    "warnings": 0,
    "info": 0
  },
  "diagnostics": []
}
```
