import re, json, urllib.request
from urllib.parse import urljoin, urlparse
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126"}
def get(url, t=15):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)[:50]
site = "https://vinosunidos.com"
st, h = get(site + "/")
hl = h.lower()
text = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
body = re.sub(r"<[^>]+>", " ", text); body = re.sub(r"\s+", " ", body)
hrefs = re.findall(r'href="([^"]+)"', h)
# interior pages (same spirit as scanner: up to 5)
links = set()
for href in hrefs:
    u = urljoin(site + "/", href); p = urlparse(u)
    if p.netloc == "vinosunidos.com" and re.search(r"(visit|tasting|event|contact|shop|club|roots|about|faq)", p.path, re.I) and "/cdn/" not in p.path:
        links.add(p.path.rstrip("/"))
interiors = []
for path in sorted(links)[:5]:
    s2, h2 = get(site + path)
    if s2 == 200: interiors.append((path, h2))
all_html = h + " ".join(x[1] for x in interiors)
all_text = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", all_html, flags=re.S))
heads = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<h[123][^>]*>(.*?)</h[123]>", all_html, re.S)]
qheads = [x for x in heads if x and ("?" in x or re.match(r"(?i)(how|what|why|when|where|who|which|can|should|do|does|is|are)\b", x))]
ld_types = re.findall(r'"@type"\s*:\s*"([^"]+)"', h)
robots_meta = " ".join(re.findall(r'<meta[^>]*name="robots"[^>]*content="([^"]*)"', h, re.I))
imgs = len(re.findall(r"<img", hl)); noalt = len(re.findall(r"<img(?![^>]*alt=)", hl))
micro = len(re.findall(r'itemtype="', hl))
sr, rob = get(site + "/robots.txt"); sl, llms = get(site + "/llms.txt"); ss, sm = get(site + "/sitemap.xml")
bots = ["gptbot","oai-searchbot","chatgpt-user","claudebot","claude-user","claude-searchbot","google-extended","perplexitybot","perplexity-user","meta-externalagent","applebot-extended","amazonbot","duckassistbot","ccbot","bytespider"]
blocked = [b for b in bots if re.search(rf"(?is)user-agent:\s*{b}\s*\n\s*disallow:\s*/\s*$", rob, re.M)] if sr==200 else []
social = sorted(set(m.group(1) for x in [h] for m in re.finditer(r"(facebook|instagram|youtube|linkedin|twitter|x\.com|tiktok|yelp|tripadvisor)\.com", " ".join(hrefs))))
out = {
 "fetch": st, "interiors": [x[0] for x in interiors],
 "jsonld": len(ld_types) > 0, "ld_types": sorted(set(ld_types))[:8],
 "org": any(t in ("Organization","LocalBusiness","Winery","Store") for t in ld_types),
 "faq_schema": "FAQPage" in ld_types, "microdata": micro,
 "robots_ok": sr == 200 and not blocked, "blocked": blocked,
 "llms": sl == 200 and len(llms) > 20 and not llms.strip().startswith("<"),
 "sitemap": ss == 200 and bool(re.search(r"<(urlset|sitemapindex)", sm)),
 "noindex": "noindex" in robots_meta.lower(), "canonical": 'rel="canonical"' in hl,
 "nosnippet": bool(re.search(r"nosnippet|max-snippet\s*:\s*0(?!\d)", robots_meta, re.I)),
 "noarchive": "noarchive" in robots_meta.lower(), "nocache": "nocache" in robots_meta.lower(),
 "text_chars": len(body.strip()),
 "title_ok": bool(re.search(r"<title>.{15,}</title>", h)),
 "desc_len": len((re.search(r'name="description"[^>]*content="([^"]*)"', h) or [None,""])[1]),
 "h1": "<h1" in hl, "imgs": imgs, "noalt": noalt,
 "og": 'property="og:' in hl, "qheads": qheads[:5], "n_qheads": len(qheads),
 "fresh_2026": "2026" in all_text, "price": bool(re.search(r"\$\s?\d{2}", all_text)),
 "social_links": social,
 "tel": "tel:" in all_html.lower(), "mailto": "mailto:" in all_html.lower(),
 "booking": bool(re.search(r"cart|checkout|book|reserve", hl)), "https": st == 200,
}
print(json.dumps(out, indent=0))
