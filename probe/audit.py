import urllib.request, json
def hit(q):
    try:
        req = urllib.request.Request(
            "https://ao-relay.aojedamedia.workers.dev/places?q=" + urllib.parse.quote(q),
            headers={"Origin": "https://aoaudit.com"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()
    except Exception as e:
        return 0, str(e)[:120]
import urllib.parse
for q in ["Vinos Unidos Napa", "The French Laundry Yountville", "Cliff Lede Vineyards Napa"]:
    s, b = hit(q)
    print(f"[{s}] {q} -> {b}")
# also the no-param case
try:
    req = urllib.request.Request("https://ao-relay.aojedamedia.workers.dev/places", headers={"Origin":"https://aoaudit.com"})
    urllib.request.urlopen(req, timeout=10)
except Exception as e:
    print("no-param ->", str(e)[:60])
