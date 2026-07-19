import urllib.request, urllib.parse, json
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
def places(q):
    req = urllib.request.Request("https://ao-relay.aojedamedia.workers.dev/places?q=" + urllib.parse.quote(q),
        headers={"Origin":"https://aoaudit.com","User-Agent":UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())
# a real, precise query for a well-known Napa winery so the demo shows real data
for q in ["Cliff Lede Vineyards, Yountville, CA", "Frog's Leap Winery, Rutherford, CA"]:
    try: print(q, "->", json.dumps(places(q)))
    except Exception as e: print(q, "-> ERR", str(e)[:80])
