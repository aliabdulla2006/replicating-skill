#!/usr/bin/env python3
"""Seedance video generation via the Kie API. Upload refs, create task, poll, download.

Usage:
  kie_seedance.py --check
  kie_seedance.py --prompt-file P.txt --out V1.mp4 --ref start.png box.png [--duration 5]
  kie_seedance.py --prompt-file P.txt --out V1.mp4 --ref a.png --dry-run

Cost discipline (CLAUDE.md sec 7): never submit trial jobs. Prompt-test in text first.
Use --dry-run to see exactly what would be sent without spending anything.
"""
import argparse, json, mimetypes, os, sys, tempfile, time, urllib.request, urllib.error, uuid

UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
CREATE = "https://api.kie.ai/api/v1/jobs/createTask"
POLL   = "https://api.kie.ai/api/v1/jobs/recordInfo"
DEFAULT_MODEL = "bytedance/seedance-1.5-pro"
MAX_BYTES = 10 * 1024 * 1024


def load_key(var):
    if os.environ.get(var):
        return os.environ[var]
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        f = os.path.join(d, ".env")
        if os.path.isfile(f):
            for line in open(f):
                line = line.strip()
                if line.startswith(var + "="):
                    return line.split("=", 1)[1].strip()
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def req(url, key, data=None, method=None, headers=None, timeout=120):
    h = {"Authorization": f"Bearer {key}",
         "User-Agent": "kie-seedance-cli/1.0 (Mozilla/5.0)",
         "Accept": "application/json"}
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} on {url}\n{e.read().decode()[:600]}")
    except urllib.error.URLError as e:
        sys.exit(f"network error on {url}: {e.reason}")


def shrink(path):
    """Return a path under MAX_BYTES. Converts to JPEG if needed."""
    if os.path.getsize(path) <= MAX_BYTES:
        return path, False
    ext = os.path.splitext(path)[1].lower()
    if ext in {".mp4", ".mov", ".webm", ".m4v", ".mkv"}:
        sys.exit(f"{path} is over 10MB — compress it externally (ffmpeg) before passing to --ref-video; PIL-based shrink only handles images")
    try:
        from PIL import Image
    except ImportError:
        sys.exit(f"{path} is over 10MB and Pillow is not installed to shrink it")
    im = Image.open(path).convert("RGB")
    out = os.path.join(tempfile.gettempdir(), f"kie_{uuid.uuid4().hex[:8]}.jpg")
    q = 92
    while q >= 60:
        im.save(out, quality=q, optimize=True)
        if os.path.getsize(out) <= MAX_BYTES:
            return out, True
        q -= 8
    sys.exit(f"could not shrink {path} under 10MB")


def upload(path, key):
    path, shrunk = shrink(path)
    name = uuid.uuid4().hex[:8] + "-" + os.path.basename(path)  # unique: parallel jobs with same filenames overwrote each other
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    b = uuid.uuid4().hex
    parts = []
    for field, val in (("uploadPath", "ecom"), ("fileName", name)):
        parts.append(
            f"--{b}\r\nContent-Disposition: form-data; name=\"{field}\"\r\n\r\n{val}\r\n".encode()
        )
    parts.append(
        f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n".encode()
    )
    parts.append(open(path, "rb").read())
    parts.append(f"\r\n--{b}--\r\n".encode())
    body = b"".join(parts)
    r = req(UPLOAD, key, data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={b}"}, timeout=300)
    d = r.get("data") or {}
    url = d.get("downloadUrl") or d.get("fileUrl") or d.get("url")
    if not url:
        sys.exit(f"upload returned no URL: {json.dumps(r)[:400]}")
    note = " (shrunk)" if shrunk else ""
    print(f"  uploaded {name}{note} -> {url}", file=sys.stderr)
    return url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify auth and print config, spends nothing")
    ap.add_argument("--dry-run", action="store_true", help="print the request body and exit, spends nothing")
    ap.add_argument("--prompt"); ap.add_argument("--prompt-file")
    ap.add_argument("--out"); ap.add_argument("--ref", nargs="*", default=[])
    ap.add_argument("--ref-video", nargs="*", default=[],
                    help="seedance-2 only: video refs (mp4). Can combine with --ref image refs.")
    ap.add_argument("--model", default=None)
    ap.add_argument("--duration", type=int, default=5)
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--resolution", default="1080p")
    ap.add_argument("--audio", action="store_true", default=True)
    ap.add_argument("--no-audio", dest="audio", action="store_false")
    ap.add_argument("--fixed-lens", action="store_true")
    ap.add_argument("--ref-mode", choices=["first_frame","refs"], default="first_frame",
                    help="seedance-2 only: first_frame anchors motion (use only 1st ref); refs uses all as design refs (no first-frame anchor). Ignored when --ref-video is set (image refs go to reference_image_urls alongside reference_video_urls).")
    ap.add_argument("--poll-every", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    key = load_key("KIE_API_KEY")
    model = a.model or load_key("KIE_MODEL") or DEFAULT_MODEL

    if not key:
        sys.exit("no KIE_API_KEY: add it to ecom/.env or export it")

    if a.check:
        print(f"KIE_API_KEY  loaded ({len(key)} chars)")
        print(f"model        {model}")
        print(f"endpoints    {UPLOAD}\n             {CREATE}\n             {POLL}")
        r = req(f"{POLL}?taskId=nonexistent_probe", key)
        print(f"auth probe   HTTP 200, code={r.get('code')} msg={r.get('msg')!r}")
        return

    if not a.out:
        sys.exit("--out is required")
    prompt = a.prompt or (open(a.prompt_file, encoding="utf-8").read() if a.prompt_file else None)
    if not prompt:
        sys.exit("need --prompt or --prompt-file")
    is_v2 = "seedance-2" in model
    max_refs = 10 if is_v2 else 2
    if len(a.ref) > max_refs:
        sys.exit(f"model {model} accepts at most {max_refs} reference images")
    duration_max = 15 if is_v2 else 12
    if not 4 <= a.duration <= duration_max:
        sys.exit(f"duration must be 4 to {duration_max} seconds")

    def build_input(url_list, video_url_list=None):
        video_url_list = video_url_list or []
        base = {"prompt": prompt, "aspect_ratio": a.aspect, "resolution": a.resolution,
                "duration": a.duration, "generate_audio": a.audio}
        if is_v2:
            # Seedance-2 supports 3 mutually-exclusive image modes plus optional video refs:
            # - first_frame_url (anchor motion): 1 image
            # - reference_image_urls (style refs): up to 10 images
            # - reference_video_urls: up to 3 videos (can COMBINE with reference_image_urls)
            if video_url_list:
                # multi-ref combo: images become reference_image_urls, videos become reference_video_urls
                # (first_frame_url can't be combined with reference_video_urls per Kie schema)
                if url_list:
                    base["reference_image_urls"] = url_list
                base["reference_video_urls"] = video_url_list
            elif url_list:
                if a.ref_mode == "first_frame":
                    base["first_frame_url"] = url_list[0]
                    # NOTE: additional refs beyond url_list[0] are DROPPED in first_frame mode
                elif a.ref_mode == "refs":
                    base["reference_image_urls"] = url_list
                else:
                    sys.exit(f"unknown --ref-mode {a.ref_mode}, use first_frame or refs")
        else:
            base["input_urls"] = url_list
            base["fixed_lens"] = a.fixed_lens
        return base

    if a.dry_run:
        preview = build_input(
            [f"<upload {os.path.basename(r)}>" for r in a.ref],
            [f"<upload {os.path.basename(v)}>" for v in a.ref_video],
        )
        preview["prompt"] = preview["prompt"][:300] + ("..." if len(prompt) > 300 else "")
        print(json.dumps({"model": model, "input": preview}, indent=2))
        print(f"\nDRY RUN. Nothing uploaded, nothing submitted, nothing spent.", file=sys.stderr)
        print(f"Prompt is {len(prompt)} chars.", file=sys.stderr)
        return

    urls = [upload(r, key) for r in a.ref]
    video_urls = [upload(v, key) for v in a.ref_video]
    body = {"model": model, "input": build_input(urls, video_urls)}
    r = req(CREATE, key, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
    if r.get("code") != 200:
        sys.exit(f"createTask failed: {json.dumps(r)[:500]}")
    task = r["data"]["taskId"]
    print(f"  task {task} submitted, model {model}", file=sys.stderr)

    start = time.time()
    last = None
    while time.time() - start < a.timeout:
        time.sleep(a.poll_every)
        d = req(f"{POLL}?taskId={task}", key).get("data") or {}
        state = d.get("state")
        if state != last:
            print(f"  [{int(time.time()-start):4d}s] {state} {d.get('progress','')}", file=sys.stderr)
            last = state
        if state == "success":
            res = d.get("resultJson")
            res = json.loads(res) if isinstance(res, str) else (res or {})
            vurls = res.get("resultUrls") or []
            if not vurls:
                sys.exit(f"success but no resultUrls: {json.dumps(d)[:400]}")
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            dl_req = urllib.request.Request(vurls[0], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(dl_req, timeout=300) as resp, open(a.out, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
            print(f"  downloaded -> {a.out} ({os.path.getsize(a.out)} bytes)", file=sys.stderr)
            print(f"  credits consumed: {d.get('creditsConsumed')}", file=sys.stderr)
            print(a.out)
            return
        if state == "fail":
            sys.exit(f"task failed: {d.get('failCode')} {d.get('failMsg')}")
    sys.exit(f"timed out after {a.timeout}s, task {task} may still finish; poll it manually")


if __name__ == "__main__":
    main()
