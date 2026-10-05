#!/usr/bin/env python3
"""Competitor-video analyzer for the `replicating` skill. Free and local, never calls a paid API.

Usage:
  replicate_analyze.py <video-file-or-URL> --out <run>/source/ [--scene 0.3] [--step 0.5] [--no-transcribe]

Writes into --out:
  reference.<ext>              the original (downloaded or copied)
  reference-SILENT.mp4         audio stripped, video stream copied (what goes to Seedance as @video_1)
  reference-SILENT-kie.mp4     only when the silent copy is over Kie's 10 MB ref limit: re-encoded 720p
  frames/t00.0.jpg ...         one frame every --step seconds
  frames/cut-NN-t.jpg          first frame after each detected hard cut
  sheet-01.jpg ...             contact sheets (timestamps burned in) for reading the clip at a glance
  cuts.jpg                     sheet of the cut frames only
  audio.wav                    16 kHz mono (only when the clip has audio)
  transcript.txt               timestamped speech (faster-whisper small), when speech is found
  analysis.json                duration, fps, size, audio, cuts, segments, flags

Needs: ffmpeg + ffprobe on PATH, yt-dlp, Pillow, (optional) faster-whisper.
"""
import argparse, json, os, re, shutil, subprocess, sys

KIE_MAX_MB = 10
SEEDANCE_MAX_S = 15
FRAME_W = 360
SHEET_COLS = 6
SHEET_MAX = 36
SOFT_SCENE = 0.12


# Small helpers (same as tools/morpheus_scan.py), kept here so this script runs on its own.
def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def duration(path):
    res = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def grab(path, t, out, width):
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
         "-vf", f"scale={width}:-2", "-q:v", "3", out])
    return os.path.isfile(out)


def sheet(frames, cols, out):
    from PIL import Image, ImageDraw
    imgs = [(t, Image.open(f).convert("RGB")) for t, f in frames]
    if not imgs:
        return False
    w, h = imgs[0][1].size
    rows_n = (len(imgs) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * w, rows_n * h), "black")
    dr = ImageDraw.Draw(canvas)
    for i, (t, im) in enumerate(imgs):
        x, y = (i % cols) * w, (i // cols) * h
        canvas.paste(im.resize((w, h)), (x, y))
        dr.rectangle([x, y, x + 46, y + 16], fill="black")
        dr.text((x + 3, y + 2), f"{t:.1f}s", fill="yellow")
    canvas.save(out, quality=85)
    return True


def clean_link(u):
    """Drop share/tracking params (?igsh=, ?mibextid=) but keep the ones that ARE the video id (?v=)."""
    base, _, q = u.strip().partition("?")
    keep = [kv for kv in q.split("&") if kv.split("=")[0] in ("v", "story_fbid", "id")]
    return base.rstrip("/") + ("?" + "&".join(keep) if keep else "")


def fetch(src, out_dir):
    """Local file -> copy. URL -> yt-dlp (YouTube needs the android client)."""
    if os.path.isfile(src):
        dst = os.path.join(out_dir, "reference" + os.path.splitext(src)[1].lower())
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy2(src, dst)
        return dst
    url = clean_link(src)
    cmd = [sys.executable, "-m", "yt_dlp", "-q", "--no-warnings", "--no-playlist", "-f", "b",
           "-o", os.path.join(out_dir, "reference.%(ext)s"), "--write-info-json"]
    if "youtu" in url:
        cmd += ["--extractor-args", "youtube:player_client=android"]
    res = run(cmd + [url], timeout=300)
    vids = [f for f in os.listdir(out_dir) if f.startswith("reference.") and not f.endswith(".json")]
    if res.returncode != 0 or not vids:
        sys.exit(f"download failed: {(res.stderr or '').strip()[-300:]}\n"
                 "Ask Ali to send the file itself (screen-record or save the reel).")
    return os.path.join(out_dir, vids[0])


def probe(path):
    res = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    data = json.loads(res.stdout or "{}")
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    num, _, den = (v.get("r_frame_rate") or "0/1").partition("/")
    fps = round(float(num) / float(den or 1), 2) if float(den or 1) else 0
    w, h = v.get("width", 0), v.get("height", 0)
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        rot = abs(int(sd.get("rotation", 0) or 0))
    if rot in (90, 270):
        w, h = h, w
    return {"width": w, "height": h, "fps": fps, "has_audio": a is not None,
            "aspect": f"{w}:{h}", "vertical_9x16": bool(h) and abs(w / h - 9 / 16) < 0.02,
            "size_mb": round(os.path.getsize(path) / 1e6, 2)}


def cuts(path, threshold):
    """Hard cuts via ffmpeg scene score. Returns sorted timestamps (s)."""
    res = run(["ffmpeg", "-hide_banner", "-i", path, "-vf", f"select='gt(scene,{threshold})',showinfo",
               "-an", "-f", "null", "-"])
    ts = sorted({round(float(m), 2) for m in re.findall(r"pts_time:([0-9.]+)", res.stderr or "")})
    return [t for t in ts if t > 0.15]


def silent(path, out_dir):
    out = os.path.join(out_dir, "reference-SILENT.mp4")
    res = run(["ffmpeg", "-v", "error", "-y", "-i", path, "-an", "-c:v", "copy", out])
    if res.returncode != 0:  # odd codecs (webm/vp9) can't stream-copy into mp4
        run(["ffmpeg", "-v", "error", "-y", "-i", path, "-an", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", out])
    kie = None
    if os.path.getsize(out) / 1e6 > KIE_MAX_MB:
        kie = os.path.join(out_dir, "reference-SILENT-kie.mp4")
        for crf in (23, 27, 31):
            run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", "scale=-2:'min(1280,ih)'", "-c:v", "libx264",
                 "-crf", str(crf), "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", kie])
            if os.path.getsize(kie) / 1e6 <= KIE_MAX_MB:
                break
    return out, kie


def transcribe(path, out_dir):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, "faster-whisper not installed, transcript skipped"
    wav = os.path.join(out_dir, "audio.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", "16000", wav])
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, info = model.transcribe(wav, vad_filter=True)
    lines = [(round(s.start, 1), round(s.end, 1), s.text.strip()) for s in segs if s.text.strip()]
    with open(os.path.join(out_dir, "transcript.txt"), "w", encoding="utf-8") as f:
        f.write(f"language: {info.language} ({info.language_probability:.2f})\n")
        for a, b, t in lines:
            f.write(f"[{a:5.1f} - {b:5.1f}] {t}\n")
    return [{"start": a, "end": b, "text": t} for a, b, t in lines], info.language


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="video file or URL (IG / TikTok / YT / FB)")
    ap.add_argument("--out", required=True, help="run folder's source/ dir")
    ap.add_argument("--scene", type=float, default=0.3, help="cut-detection threshold (lower = more cuts)")
    ap.add_argument("--step", type=float, default=0.5, help="seconds between sampled frames")
    ap.add_argument("--no-transcribe", action="store_true")
    a = ap.parse_args()

    out = os.path.abspath(a.out)
    fdir = os.path.join(out, "frames")
    os.makedirs(fdir, exist_ok=True)

    ref = fetch(a.src, out)
    dur = round(duration(ref), 2)
    info = probe(ref)
    cut_ts = cuts(ref, a.scene)
    # dark / night footage scores low on scene change: a second, looser pass catches the shots the main pass misses
    soft_ts = [t for t in cuts(ref, SOFT_SCENE) if all(abs(t - c) > 0.2 for c in cut_ts)] if a.scene > SOFT_SCENE else []

    frames, t = [], 0.0
    while t < dur - 0.05:
        f = os.path.join(fdir, f"t{t:05.1f}.jpg")
        if grab(ref, t, f, FRAME_W):
            frames.append((t, f))
        t = round(t + a.step, 2)
    sheets = []
    for i in range(0, len(frames), SHEET_MAX):
        p = os.path.join(out, f"sheet-{i // SHEET_MAX + 1:02d}.jpg")
        if sheet(frames[i:i + SHEET_MAX], SHEET_COLS, p):
            sheets.append(os.path.basename(p))
    cut_frames = []
    for n, ct in enumerate(sorted(cut_ts + soft_ts), 1):
        tag = "soft" if ct in soft_ts else "cut"
        f = os.path.join(fdir, f"{tag}-{n:02d}-{ct:05.2f}.jpg")
        if grab(ref, min(ct + 0.05, max(dur - 0.05, 0)), f, FRAME_W):
            cut_frames.append((ct, f))
    if cut_frames:
        sheet(cut_frames, min(SHEET_COLS, len(cut_frames)), os.path.join(out, "cuts.jpg"))

    sil, kie = silent(ref, out)

    speech, lang = None, None
    if info["has_audio"] and not a.no_transcribe:
        speech, lang = transcribe(ref, out)

    bounds = [0.0] + cut_ts + [dur]
    segments = [{"n": i + 1, "start": bounds[i], "end": bounds[i + 1], "len": round(bounds[i + 1] - bounds[i], 2)}
                for i in range(len(bounds) - 1)]
    flags = []
    if dur > SEEDANCE_MAX_S:
        flags.append(f"OVER {SEEDANCE_MAX_S}s: Seedance 2.0 fast max is {SEEDANCE_MAX_S}s. Split by segment or trim.")
    if dur < 4:
        flags.append("UNDER 4s: Seedance minimum is 4s, pad or extend the last beat.")
    if not info["vertical_9x16"]:
        flags.append(f"NOT 9:16 ({info['aspect']}): output will still be 9:16, framing will reflow.")
    if cut_ts:
        flags.append(f"{len(cut_ts)} hard cut(s): check cuts.jpg, Seedance may merge or drop cuts.")
    if soft_ts:
        flags.append(f"{len(soft_ts)} soft cut(s) at {soft_ts} (dark footage or a fast move): check each in cuts.jpg. "
                     "If it is a new shot, every swapped object in it needs ref coverage.")
    if info["has_audio"]:
        flags.append("Has audio: always send reference-SILENT*.mp4 to Kie, never the original.")
    ref_for_kie = kie or sil
    if os.path.getsize(ref_for_kie) / 1e6 > KIE_MAX_MB:
        flags.append("Silent copy still over 10 MB after re-encode: trim it before uploading.")

    report = {
        "source": a.src, "reference": os.path.basename(ref), "duration_s": dur, **info,
        "cuts_s": cut_ts, "soft_cuts_s": soft_ts, "segments": segments, "scene_threshold": a.scene,
        "frames_every_s": a.step, "frame_count": len(frames), "sheets": sheets,
        "cut_sheet": "cuts.jpg" if cut_frames else None,
        "silent_ref": os.path.basename(sil), "kie_ref": os.path.basename(ref_for_kie),
        "kie_ref_mb": round(os.path.getsize(ref_for_kie) / 1e6, 2),
        "speech_language": lang if isinstance(lang, str) and speech is not None else None,
        "speech": speech if isinstance(speech, list) else None,
        "transcript_note": lang if speech is None and lang else None,
        "flags": flags,
    }
    with open(os.path.join(out, "analysis.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: report[k] for k in ("duration_s", "aspect", "fps", "has_audio", "cuts_s", "soft_cuts_s",
                                             "sheets", "kie_ref", "kie_ref_mb", "flags")}, indent=2))
    if speech:
        print("speech:", " | ".join(f"[{s['start']}] {s['text']}" for s in speech))


if __name__ == "__main__":
    main()
