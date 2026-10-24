#!/usr/bin/env python3
"""Free monthly pipeline: IHMCL VC-wise PDFs -> data/roshi_feed.js (loaded by the Roshi app via jsDelivr)."""
import re, json, hashlib, subprocess, urllib.request, urllib.parse, os, datetime, tempfile
PAGE = "https://ihmcl.co.in/etc-transaction-reports/"
UA = "RoshiTransportIntelligence/1.0 (low-volume public-data research)"
KEEP_MONTHS = 14   # browser localStorage is ~5 MB; ~160 KB per month
MON = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}
NUM = re.compile(r'^(-|\d[\d,]*)$')

def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=90).read()

def month_of(url):
    n = url.rsplit('/', 1)[-1].lower()
    if any(x in n for x in ('annual', 'mlff', 'vc_wise')) or n.endswith('.zip'): return None
    y = re.search(r'(20\d\d)', n); m = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', n)
    return f"{y.group(1)}-{MON[m.group(1)]:02d}" if y and m else None

def parse(text, month):
    out = []
    for line in text.splitlines():
        t = line.split(); n = []
        while t and NUM.match(t[-1]) and len(n) < 14: n.insert(0, t.pop())
        if len(n) != 14 or not t: continue
        v = [0 if x == '-' else int(x.replace(',', '')) for x in n]
        if v[12] < v[2] + v[4]: continue
        out.append({"m": month, "l": " ".join(t), "c": v[0], "lcv": v[2], "bt": v[4], "a3": v[6], "a4": v[8], "o": v[10], "t": v[12]})
    return out

def main():
    os.makedirs("data", exist_ok=True)
    html = get(PAGE).decode("utf8", "ignore")
    links = {}
    for h in re.findall(r'href=["\']([^"\']+\.pdf)["\']', html):
        m = month_of(h)
        if m: links.setdefault(m, h)
    state = json.load(open("data/state.json")) if os.path.exists("data/state.json") else {}
    rows = json.load(open("data/rows.json")) if os.path.exists("data/rows.json") else {}
    for m, url in sorted(links.items())[-KEEP_MONTHS:]:
        blob = get(urllib.parse.quote(url, safe=":/%")); h = hashlib.sha256(blob).hexdigest()
        if state.get(m, {}).get("sha256") == h: continue            # unchanged, skip reprocessing
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(blob); f.flush()
            txt = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
        parsed = parse(txt, m)
        if len(parsed) < 300: print("SKIP", m, "only", len(parsed), "rows parsed"); continue
        rows[m] = parsed
        state[m] = {"url": url, "sha256": h, "retrieved": datetime.datetime.utcnow().isoformat() + "Z", "rows": len(parsed)}
    keep = sorted(rows)[-KEEP_MONTHS:]
    flat = [r for m in keep for r in rows[m]]
    json.dump({m: rows[m] for m in keep}, open("data/rows.json", "w"), separators=(",", ":"))
    json.dump(state, open("data/state.json", "w"), indent=1)
    gen = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()[:16]
    open("data/roshi_feed.js", "w").write("window.ROSHI_FEED=" + json.dumps({"generated": gen, "source": PAGE, "rows": flat}, separators=(",", ":")) + ";")
    print("months", keep[-3:], "rows", len(flat))

if __name__ == "__main__": main()
