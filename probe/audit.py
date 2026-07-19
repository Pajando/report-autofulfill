import os, json, urllib.request

KEY = os.environ.get("GEMINI_API_KEY", "")
print("key present:", bool(KEY), "| length:", len(KEY))

def try_endpoint(name, url, payload=None):
    try:
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"},
            data=json.dumps(payload).encode() if payload else None)
        with urllib.request.urlopen(req, timeout=25) as r:
            body = json.loads(r.read().decode())
            return name, r.status, body
    except urllib.error.HTTPError as e:
        return name, e.code, {"error": e.read().decode()[:200]}
    except Exception as e:
        return name, 0, {"error": str(e)[:200]}

# 1) classic Gemini API: list models
n, s, b = try_endpoint("generativelanguage:listModels",
    f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}")
models = [m["name"] for m in b.get("models", [])][:5] if s == 200 else b
print(f"[{s}] {n} ->", models)

# 2) tiny real generation to prove end-to-end
if s == 200:
    flash = next((m["name"] for m in b.get("models", []) if "flash" in m["name"] and "preview" not in m["name"]), None) or "models/gemini-3-flash-preview"
    n2, s2, b2 = try_endpoint("generateContent",
        f"https://generativelanguage.googleapis.com/v1beta/{flash}:generateContent?key={KEY}",
        {"contents": [{"parts": [{"text": "Reply with exactly: AO-PROBE-OK"}]}]})
    txt = ""
    try: txt = b2["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception: txt = str(b2)[:200]
    print(f"[{s2}] {n2} using {flash} ->", txt)
