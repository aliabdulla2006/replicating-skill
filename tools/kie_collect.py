"""Collect already-submitted Kie jobs (image or video) without paying again.

Usage: python tools/kie_collect.py TASK_ID OUT_PATH [TASK_ID OUT_PATH ...] [--wait SECONDS]
Polls each task; downloads the result when state == success. Prints the state of the rest.
"""
import sys, os, json, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import kie_seedance as k


def fetch(task, key):
    return k.req(f"{k.POLL}?taskId={task}", key).get("data") or {}


def download(d, out):
    res = d.get("resultJson")
    res = json.loads(res) if isinstance(res, str) else (res or {})
    urls = res.get("resultUrls") or []
    if not urls:
        return False
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    rq = urllib.request.Request(urls[0], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(rq, timeout=600) as r, open(out, "wb") as f:
        f.write(r.read())
    return True


def main():
    args = sys.argv[1:]
    wait = 0
    if "--wait" in args:
        i = args.index("--wait"); wait = int(args[i + 1]); del args[i:i + 2]
    pairs = list(zip(args[0::2], args[1::2]))
    key = k.load_key("KIE_API_KEY")
    start = time.time()
    pending = dict(pairs)
    while True:
        for task, out in list(pending.items()):
            d = fetch(task, key)
            st = d.get("state")
            if st == "success":
                ok = download(d, out)
                print(f"{task[:8]} success -> {out} ({os.path.getsize(out) if ok else 0} bytes)", flush=True)
                pending.pop(task)
            elif st == "fail":
                print(f"{task[:8]} FAILED: {d.get('failMsg')}", flush=True)
                pending.pop(task)
        if not pending or time.time() - start > wait:
            break
        time.sleep(20)
    for task in pending:
        print(f"{task[:8]} still {fetch(task, key).get('state')}", flush=True)


if __name__ == "__main__":
    main()
