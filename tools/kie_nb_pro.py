#!/usr/bin/env python3
"""Nano Banana Pro (nano-banana-pro) image generation via Kie API.

Usage:
  kie_nb_pro.py --prompt-file P.txt --out OUT.png --ref box-front.png [--ref other.png ...]

Cost discipline: single call = one image. NEVER submit trial jobs.
"""
import argparse, json, mimetypes, os, sys, tempfile, time, urllib.request, urllib.error, uuid

UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
CREATE = "https://api.kie.ai/api/v1/jobs/createTask"
POLL   = "https://api.kie.ai/api/v1/jobs/recordInfo"
MODEL  = "nano-banana-pro"
MAX_BYTES = 10 * 1024 * 1024


def load_key(var="KIE_API_KEY"):
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
    sys.exit(f"no {var}: set it in env or in .env")


def req(url, key, data=None, method=None, headers=None, timeout=120):
    h = {"Authorization": f"Bearer {key}",
         "User-Agent": "kie-nbpro-cli/1.0 (Mozilla/5.0)",
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
    if os.path.getsize(path) <= MAX_BYTES:
        return path, False
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
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--poll-every", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--task", help="resume polling an already-submitted taskId (spends nothing)")
    a = ap.parse_args()

    key = load_key("KIE_API_KEY")
    prompt = open(a.prompt_file, encoding="utf-8").read()

    if a.dry_run:
        print(json.dumps({"model": MODEL, "input": {"prompt": prompt[:200]+"...",
             "image_urls": ["<uploads>"], "output_format": "png", "image_size": a.aspect}}, indent=2))
        print("DRY RUN. Nothing spent.", file=sys.stderr)
        return

    if a.task:
        task = a.task
        print(f"  resuming task {task}", file=sys.stderr)
    else:
        task = None
    if not task:
      urls = [upload(r, key) for r in a.ref]
      body = {"model": MODEL, "input": {
        "prompt": prompt,
        "image_urls": urls,
        "image_input": urls,
        "output_format": "png",
        "image_size": a.aspect,
        "aspect_ratio": a.aspect,
        "resolution": "2K",
      }}
      r = req(CREATE, key, data=json.dumps(body).encode(),
              headers={"Content-Type": "application/json"})
      if r.get("code") != 200:
          sys.exit(f"createTask failed: {json.dumps(r)[:500]}")
      task = r["data"]["taskId"]
      print(f"  task {task} submitted, model {MODEL}", file=sys.stderr)
      os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
      with open(a.out + ".task.txt", "w") as tf:
          tf.write(task + "\n")

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
            urls = res.get("resultUrls") or []
            if not urls:
                sys.exit(f"success but no resultUrls: {json.dumps(d)[:400]}")
            os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
            dl_req = urllib.request.Request(urls[0], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(dl_req, timeout=300) as r2, open(a.out, "wb") as f:
                f.write(r2.read())
            print(f"OK saved {a.out} ({os.path.getsize(a.out)} bytes)")
            return
        if state == "fail":
            sys.exit(f"task failed: {json.dumps(d)[:500]}")
    sys.exit(f"timed out after {a.timeout}s; resume with: --task {task} --out {a.out}")


if __name__ == "__main__":
    main()
