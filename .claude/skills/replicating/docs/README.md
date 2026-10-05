# The 4 prompt docs (Elias), bundled for the replicating skill

Saved 2026-10-04 from the user's upload, word for word. The only change is cleanup of the Google-Docs markdown escapes (`\#` became `#`, `\-` became `-`, and so on). Read-only: never edit these files.

## the user's ruling (2026-10-04)

**Inside this skill the 4 docs are followed exactly as written, even where they clash with our other rules** (CLAUDE.md locks, kernels, memories, the `realism-image-prompt` skill). Do not apply house adaptations from `prompts/_kernels/`.

**The one exception kept from our rules:** GPT Image runs ONE generation per image, never four.

| # | File | Stage |
|---|---|---|
| 1 | `01-SEEDENCE-BACKGROUND-PROMPT.md` | Video: recreate the competitor clip (@video_1) and change only the swapped elements. STEP 1 scene analysis, then the MANDATORY PROMPT TEMPLATE verbatim, LOCKED RULES 1-10, two-version default, CRITICAL DON'TS. |
| 2 | `02-CLAUDE-CONTEXT-PROMPT.md` | Video from scratch (13-section architecture, RULES 1-14, FAILURE 1-10) and every image EDIT (CRITICAL KEEP / CRITICAL CHANGE / DO NOT). Also the fix workflow. |
| 3 | `03-ENVIRONMENT-CONTEXT-PROMPT.md` | Every real-photo image ref (start frame, person, environment): STEP 1-5, output order, gpt_image_2_5, 1k, 9:16. |
| 4 | `04-ADVANCED-REALISM-PROMPT-STRUCTURE.md` | Every real-photo image ref: REALISM BLOCK pasted unchanged, scene lighting swaps, NEVER USE THESE WORDS. gpt_image_2_5, 1k, 9:16 or 3:4. |

## Which doc when

- **Video, the clip can be the reference (default):** doc 1 only.
- **Video, the clip can't be the reference** (doc 1 scope doesn't fit, e.g. the whole video must change, or the clip is unusable as a reference): doc 2's 13 sections.
- **New real-photo image** (start frame, person, environment): docs 3 + 4 together. Doc 3 builds the niche; doc 4's REALISM BLOCK is pasted unchanged.
- **Image edit** (box swap on a frame grab, cleaning a ref): doc 2's KEEP / CHANGE / DO NOT.
- **Clean studio packshot** (white background): doc 4 says its realism rules don't apply. Write it with doc 2's image section.
