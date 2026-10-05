# Replicating: a Claude Code skill that remakes competitor videos with Seedance 2.0 fast

Send Claude a competitor reel (an Instagram / TikTok / YouTube / Facebook link, or the mp4 file) and say what to change: "replicate this video, swap their team for ours". The skill then:

1. **Downloads and analyzes the clip** (free, local): duration, hard cuts and soft cuts, frames every 0.5 s, contact sheets, a silent copy, and a speech transcript.
2. **Asks only the necessary questions** (team / product, outfit, logo style ...).
3. **Builds the image refs first.** It edits frames of the source with Nano Banana Pro (boxes, logo, outfit, projection), one image at a time, each after your "fire".
4. **Writes the Seedance prompt** exactly per the 4 prompt docs in `.claude/skills/replicating/docs/`, then dry-runs it for free.
5. **Fires one video** on Kie.ai (`bytedance/seedance-2-fast`, 720p, 9:16, silent), using the competitor clip as `@video_1` plus the image refs.
6. **Reviews every shot** of the render, offers a free ffmpeg trim for small leaks, and patches only the failing part if a re-render is needed.

Nothing paid is ever fired without your explicit "fire" for that one job.

## What's in here

| Path | What it is |
|---|---|
| `.claude/skills/replicating/SKILL.md` | The skill: the full step-by-step method Claude follows |
| `.claude/skills/replicating/docs/` | The 4 prompt docs, word for word. Inside this skill they win over any other rule. `docs/README.md` maps which doc is used at which stage. |
| `.claude/skills/replicating/templates/` | Files copied into every run: analysis, questions, the two prompt templates, run log |
| `tools/replicate_analyze.py` | Link-or-file downloader + analyzer (yt-dlp + ffmpeg + faster-whisper). Free. |
| `tools/kie_seedance.py` | Seedance video on Kie: upload refs + reference video, create the task, poll, download. `--dry-run` and `--check` are free. |
| `tools/kie_nb_pro.py` | Nano Banana Pro image edits on Kie (for the image refs) |
| `tools/kie_collect.py` | Re-collects a Kie task that timed out while polling (no new charge) |
| `examples/` | Two real runs (LA Dodgers car door projector): the analysis, the run log with every verdict, and every prompt. Text only. |

## Install (give this to your Claude Code)

1. Open your project folder in Claude Code. Copy `.claude/skills/replicating/` into your project's `.claude/skills/`, and copy the 4 files in `tools/` into your project's `tools/` folder. The commands in the skill run from the project root, so `tools/` must sit at the root.
2. Install the requirements:
   - Python 3.10+, then `pip install -r requirements.txt`
   - ffmpeg + ffprobe on PATH. Windows: `choco install ffmpeg` or `winget install Gyan.FFmpeg`. Mac: `brew install ffmpeg`.
3. Create a `.env` file in the project root (see `.env.example`) with your own `KIE_API_KEY` from kie.ai. Never commit it.
4. Check everything (free): `python tools/kie_seedance.py --check` should print `auth probe HTTP 200`.
5. Restart Claude Code (or open a new chat). The skill `replicating` shows up in the skills list.

Optional: if you use the Higgsfield connector in Claude, the skill can run the image edits there instead of Kie. Just say "use Higgsfield".

## How to use it

> replicate this video: https://www.instagram.com/reel/XXXX/ . It's their Barcelona version, make it LA Dodgers: swap the boxes, the banner and her outfit, and the projected logo at the end. Remove the caption.

Each run lives in `products/<product>/<niche>/replications/<date>-<slug>/`, with `source/`, `refs/`, `prompts/` and `outputs/`, plus `ANALYSIS.md` and `RUN-LOG.md`. Change that path in `SKILL.md` step 1 if your folders are organized differently.

## Downloading from an Instagram link (how it works)

`replicate_analyze.py` accepts a link directly:

```
python tools/replicate_analyze.py "https://www.instagram.com/p/XXXX/" --out "products/<p>/replications/<run>/source"
```

- It strips tracking parameters (`?igsh=`, `?mibextid=`) and downloads with `yt-dlp` (`-f b`, best single file). YouTube uses the android client.
- Downloads are anonymous: no login or cookies. That works for most public reels and posts. Instagram sometimes blocks anonymous downloads (a private or age-gated post, or rate limiting after many downloads in a row). If that happens, the script says so; save the reel with a site like SaveClip and pass the mp4 file instead.
- Keep `yt-dlp` up to date (`pip install -U yt-dlp`). Instagram changes often and old versions break.

## Costs seen (Kie, Oct 2026)

| Job | Credits |
|---|---|
| Nano Banana Pro image edit | ~20 to 25 |
| Seedance 2.0 fast, 720p, with a reference video | ~28 to 30 per second (9 s = 255, 12 s = 360) |

## Lessons already built in (from real runs)

- **Every visible face.** Seedance only swaps what the refs show. In run 1 the box SIDES kept the competitor's crest because the ref only showed the fronts. Refs and the prompt must cover every panel that comes into view.
- **Every shot it appears in.** In run 2 a dark night shot hid a cut, and the competitor's logo survived for 0.8 s in it. The analyzer now reports `soft_cuts_s`, and each shot containing a swapped object needs ref coverage or an explicit mention.
- **Don't name the unwanted thing.** Naming the competitor's brand in an image edit's DO NOT list kept it alive. Patch by editing the failed image itself and describing only what the area should become.
- **Use your own brand on the packaging,** never the competitor's (theirs was "DriveTouchdown"; ours for baseball is "Walk-Off Lights").
