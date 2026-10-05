---
name: replicating
description: Replicate a competitor's video for one of our products with Seedance 2.0 fast on Kie.ai, strictly following the 4 Elias prompt docs. Use when the user says "replicate this video", "replicate", "copy this competitor video", "recreate this reel", "make our version of this", or sends a competitor reel (file or IG / TikTok / YT / FB link) to remake. Analyzes the clip, asks only the necessary questions, builds any image refs first, then writes the Seedance prompt exactly per the docs.
---

# Replicating (competitor video into our Seedance 2.0 fast video)

## THE RULE OF THIS SKILL (rule set 2026-10-04)

Follow the 4 docs in `docs/` **exactly as they describe it, even where they clash with our other rules**. Inside this skill, do NOT apply CLAUDE.md prompt locks, kernel house adaptations, prompt memories or the `realism-image-prompt` skill. Where the docs say something, the docs win.

**Only exception kept from our rules:** GPT Image = ONE generation per image, never four.

Read `docs/README.md` (which doc at which stage), then the doc(s) for the stage you're on. Re-read the doc before writing each prompt; don't work from memory.

## 1. Intake

- Ask which product only if it's unclear.
- Make the run folder `products/<product>/replications/<YYYY-MM-DD>-<slug>/` with `source/ refs/ prompts/ outputs/`, then copy in `templates/ANALYSIS.md` and `templates/RUN-LOG.md`.

## 2. Analyze (free)

```
python tools/replicate_analyze.py "<file-or-URL>" --out "products/<product>/replications/<run>/source"
```

The script writes duration, cuts, frames every 0.5 s, contact sheets, `cuts.jpg`, a silent copy of the clip, the transcript and `analysis.json`. Read every sheet and cut frame yourself.

Fill `ANALYSIS.md` and give the user **doc 1 STEP 1 exactly**, in 3-5 lines:
- duration
- number of scenes / hard cuts
- foreground elements to preserve
- elements being replaced
- text overlays (they will be removed)
- safety / brand-safety / IP flags: flag them briefly, don't refuse, offer options

## 3. Ask (only what's necessary)

Doc limits apply:
- Doc 2: at most 2-3 clarifying questions, ideally none, and no questions about pricing, branding or business decisions.
- Doc 1: when the brief is ambiguous, EITHER ask one clarifying question OR deliver two distinct versions, never both.

Use `templates/QUESTIONS.md` and AskUserQuestion.

## 4. Image refs FIRST (only if the video needs them)

Decide which refs the video needs: our product image, plus any start frame, person or environment ref. Reuse existing files from `products/<product>/` when they fit.

**Every visible face (lesson 2026-10-05, Dodgers V1).** Seedance only swaps what the refs show. Any face of a swapped object that the ref doesn't show keeps the competitor's design from @video_1. In the Dodgers run, the ref showed box fronts only, so Barça crests survived on the box SIDES when the box was lifted and when the boxes behind it were revealed. Before writing image refs:
1. Scrub the source frames and list every face of every swapped object that ever becomes visible: sides, top, back and bottom of a lifted or tilted box, the packaging behind a pulled item, the back of a turned product, a door's inner panel, anything that rotates.
2. Make sure the refs cover each of those faces. Either pick an edit frame where the object is already turned (e.g. the frame where she tips the box into the cart), or add one more ref showing the swapped object at an angle with its side panel visible.
3. In the video prompt's change (1), add one sentence covering every panel of the swapped object, including the panels revealed by the motion. Say what each panel looks like.

**Every shot it appears in (lesson 2026-10-05, Dodgers V2).** In the second Dodgers run, the night scene was really three shots: the door swinging open, a wide shot and a top-down shot. Only the top-down shot had a ref, so the competitor's orange Longhorn survived in the door-opening shot from 8.6 to 9.3 s. The main cut detector also missed those shots because night footage scores low. Rules:
4. Check the analyzer's `soft_cuts_s` as well as `cuts_s`. Look at every soft-cut frame; if it starts a new shot or angle, treat it as its own shot.
5. List every shot where each swapped object appears (the projection, the logo, the box, the outfit). For each one, either a ref covers it, or change (1) names that shot explicitly ("in the shot where the door swings open, ..., and in the wide shot ..., and in the top-down shot ...").
6. When a shot's angle differs a lot from the ref (close-up while the door opens vs top-down), make an extra ref from a frame of that shot. For each image that has to be generated, one at a time:

- **New real-photo image:** doc 3 STEP 1-5 + doc 4.
  - Build the prompt in doc 3's OUTPUT FORMAT order: `[WHO + WHERE (niched setting) + WHAT THEY'RE DOING + FRAMING] + niche signals (5-6, concrete) + LIGHTING line + REALISM block`.
  - Paste doc 4's REALISM BLOCK **unchanged**, including its dashes. Use doc 4's SCENE LIGHTING SWAPS for store and outdoor scenes.
  - Never use the doc 4 NEVER USE words.
  - Output ONE version, no "level" comparisons.
  - Engine: `gpt_image_2_5` (GPT-Image), 1k, 9:16 (or 3:4 per doc 4). **ONE generation.**
- **Image edit:** doc 2's 3-block structure: CRITICAL KEEP / CRITICAL CHANGE / DO NOT. Per doc 2, DO NOT only names failure modes and objects actually present.
- **Clean studio packshot:** not a real-photo image (doc 4), so write it with doc 2's image section.

Save each prompt to `prompts/img-<slot>-v1.txt` and show it in a code block. Ask the user "fire?", fire one, then show the result before moving to the next image. Log it in `RUN-LOG.md`.

How to fire an image:
- **Image edit on Kie (Nano Banana Pro):** first grab a full-res frame, e.g. `ffmpeg -ss 1.0 -i source/reference.mp4 -frames:v 1 source/full-1.0s.png`. Then run `python tools/kie_nb_pro.py --prompt-file <run>/prompts/img-1-v1.txt --out <run>/refs/img-1-v1.png --ref <run>/source/full-1.0s.png --aspect 9:16`. Add `--dry-run` first to check the request for free.
- **Higgsfield (if the user asks for it):** use the Higgs MCP. Check `list_workspaces` is the user's own account, `media_upload` the frame (PUT with header `If-None-Match: *`), `media_confirm`, then `generate_image` with model `nano_banana_pro` (edits) or `gpt_image_2_5` (new real-photo images), aspect 9:16, count 1. Poll with `jobs_wait` and download the result URL into `refs/`.
- **Patch a failed image:** edit the failed image itself, not the source frame, so what came out right is kept. Change only the failing element (doc 2 "fix" rule). Never name the unwanted thing in DO NOT unless it's actually in the image (doc 2 RULE 1); in the Dodgers run, naming the competitor brand in DO NOT kept it alive.

## 5. Video prompt

### A. Recreate + swap (default): doc 1, verbatim template

Fill in doc 1's MANDATORY PROMPT TEMPLATE exactly (`templates/PROMPT-recreate-swap.txt`):

- Opening ownership clause: "This is a recreation of my own original ~X-second vertical iPhone UGC video. I own @video_1 and all rights to it." (LOCKED RULE 1)
- "@video_1 is the full reference for everything in the output", followed by a foreground inventory of the actual elements seen in the clip. Don't invent anything and don't describe it beat by beat. (RULES 2, 9)
- "Keep the entire foreground absolutely identical to @video_1."
- "The ONLY changes:"
  - (1) the env/element swap. Our product goes here, written specific and visually rich: materials, colors, lighting tone, props. (RULES 3, 10) Cover EVERY face of each swapped object that becomes visible, not just the front (see "Every visible face" in step 4).
  - (2) the text strip, exactly as written. (RULE 4)
  - (3) the audio strip, exactly as written: completely silent output. (RULE 5)
- Close: "X seconds total, vertical 9:16. Ultra-realistic iPhone UGC look throughout, completely silent output with zero text." (RULES 6-8)
- **NEVER** use the CRITICAL KEEP / CRITICAL CHANGE / DO NOT blocks here, and never add anything outside the template.
- **Sensitive context:** layer in doc 1's DEFENSIVE FRAMING phrases.
- **Multiple scenes needing different swaps:** use the MULTI-SCENE wording, tell the user it's a stretch case, and recommend the fallback: split the clip in CapCut, generate each scene separately, recombine in post.
- **TWO-VERSION DEFAULT:** if the swap direction is open to interpretation, deliver Version A / Version B with meaningfully different aesthetics and a short explanation of each vibe. If the brief is specific, deliver one prompt.
- **Output order (doc 1 INTERACTION FLOW):** the analysis, then the prompt(s) in a copy-paste code block, then a brief outro if relevant. No disclaimers or filler.

### B. From scratch: doc 2, 13 sections

Use `templates/PROMPT-from-scratch.txt`. It holds the 13 sections in order:

1. OPENING LINE
2. CAMERA & FRAMING
3. IMAGE QUALITY
4. SETTING
5. CHARACTER
6. BEHAVIOR
7. ACTION & DIALOGUE TIMED
8. DIALOGUE DELIVERY
9. VOICE PROFILE
10. SOUND DESIGN TIMESTAMPED
11. STYLE
12. CRITICAL RULES (5-10)
13. DO NOT

Apply all of RULES 1-14 and guard against FAILURES 1-10. In particular:
- Put the @image tags at the top.
- Repeat the product lock 3x: "Keep @product 100% identical to its reference image — same design, same proportions, same details. Do NOT redraw or modify it."
- Time everything to the second.
- Allow about 2.5-3 words per second of dialogue.
- No music unless the user asks.
- Repeat the key locks 3x.

After the prompt, add doc 2's note: (a) the choices made, (b) the failure risks, (c) what to try if it fails.

Save prompts with the Write tool as `prompts/video-v1.txt` (or `-A` / `-B`). Never use PowerShell `Out-File`, which adds a BOM to the prompt.

## 6. Fire (Seedance 2.0 fast on Kie)

```
python tools/kie_seedance.py --dry-run --prompt-file <run>/prompts/video-v1.txt --out <run>/outputs/V1.mp4 \
  --ref <image refs in @image order> --ref-video <run>/source/reference-SILENT.mp4 \
  --model bytedance/seedance-2-fast --duration <X> --aspect 9:16 --resolution 720p --ref-mode refs --no-audio
```

- **`--no-audio`** matches doc 1 change (3), a silent output. For a doc 2 prompt with sound design, leave audio on.
- **Duration** is 4-15 s, a whole number.
- **`--ref-mode refs`** is needed so Kie keeps every image ref. Without it the script drops all images after the first.
- **Reference video:** send the silent copy (`-kie.mp4` when the analyzer made one, which happens when the clip is over 10 MB).
- **Clips over 15 s:** split them into segments per doc 1's multi-scene fallback.
- **Check the dry-run** lists every image under `reference_image_urls` and the video under `reference_video_urls`.
- **Fire gate:** show the user the prompt, refs and estimated credits (about 30 per second at 720p with a video ref) and ask "fire?". Fire one on his go. Log the task id. If it times out, run `python tools/kie_collect.py <task> <out>`.

## 6b. Review the render (free)

```
python tools/replicate_analyze.py "<run>/outputs/V1.mp4" --out "<run>/outputs/review" --no-transcribe
```

Read the review sheets next to `source/sheet-*.jpg`. Check EVERY shot, including the soft-cut shots: is the competitor's logo, product or brand gone in each one, do the swaps match the refs, is there zero text? If a leak lasts under a second, grab frames every 0.1 s around it to find its exact span. Offer a free ffmpeg trim when cutting that span still leaves a clean edit, e.g.:

```
ffmpeg -i V1.mp4 -filter_complex "[0:v]trim=0:A,setpts=PTS-STARTPTS[a];[0:v]trim=start=B,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 17 -pix_fmt yuv420p V1-trim.mp4
```

## 7. Fix loop (doc 2 WORKFLOW SHORTCUTS)

When the user says what failed, don't restart. Diagnose (a) trigger words, (b) the structural concept, (c) which FAILURE pattern it matches. Patch only that section, show the diff or the full corrected prompt, save it as v2, and ask "fire?".

When the user says "lock [X]" or "same setup as previous clip", apply doc 2's shortcut in every later prompt of the run.
