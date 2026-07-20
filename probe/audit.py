import urllib.request, urllib.parse
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
def relay(target):
    url = "https://ao-relay.aojedamedia.workers.dev/?url=" + urllib.parse.quote(target)
    try:
        req = urllib.request.Request(url, headers={"Origin":"https://aoaudit.com","User-Agent":UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8","replace")
            return r.status, len(body), ("<html" in body.lower() or "<!doctype" in body.lower() or "<title" in body.lower())
    except urllib.error.HTTPError as e:
        return e.code, 0, False
    except Exception as e:
        return 0, 0, str(e)[:80]
for t in ["https://example.com", "https://tgbarbers.com", "https://cliffledevineyards.com"]:
    s, n, h = relay(t)
    print(f"RELAY {t} -> status={s} bytes={n} has_html={h}")
