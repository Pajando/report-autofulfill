import re, json, urllib.request
from urllib.parse import urljoin, urlparse
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126"}
def get(url, timeout=15):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)[:60]
def digest(html):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    heads = [re.sub(r"<[^>]+>", "", h).strip()[:70] for h in re.findall(r"<h[123][^>]*>(.*?)</h[123]>", text, re.S)]
    body = re.sub(r"<[^>]+>", " ", text); body = re.sub(r"\s+", " ", body).strip()
    return {
        "title": (re.search(r"<title[^>]*>(.*?)</title>", html, re.S) or [None, ""])[1].strip()[:70],
        "heads": [h for h in heads if h][:6],
        "tel": "tel:" in html.lower(), "mailto": "mailto:" in html.lower(),
        "phone_text": bool(re.search(r"\(\d{3}\)\s?\d{3}[-. ]\d{4}|\d{3}[-.]\d{3}[-.]\d{4}", body)),
        "email_text": bool(re.search(r"[\w.+-]+@[\w-]+\.\w+", body)),
        "text": body[:500],
    }
site = "https://vinosunidos.com"
st, home = get(site + "/")
out = {"home_status": st}
links = set()
for href in re.findall(r'href="([^"#?]+)"', home):
    u = urljoin(site + "/", href)
    p = urlparse(u)
    if p.netloc == "vinosunidos.com" and not re.search(r"\.(jpg|png|css|js|svg|webp|pdf)$", p.path, re.I):
        path = p.path.rstrip("/")
        if path and path != "" and "/cdn/" not in path and "/products/" not in path:
            links.add(path)
keep = [l for l in sorted(links) if re.search(r"about|story|contact|event|club|visit|tasting|faq|shipping|team|press|blog|pages", l, re.I)] or sorted(links)
out["all_paths"] = sorted(links)[:25]
pages = {}
for path in keep[:10]:
    s2, h2 = get(site + path)
    pages[path] = {"status": s2, **(digest(h2) if s2 == 200 else {})}
out["pages"] = pages
print(json.dumps(out, indent=0))
