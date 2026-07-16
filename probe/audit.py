import re, json, urllib.request
def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)
site = "https://vinosunidos.com"
st, html = get(site + "/")
out = {"fetch": st, "bytes": len(html)}
if st == 200:
    hl = html.lower()
    ld_types = re.findall(r'"@type"\s*:\s*"([^"]+)"', html)
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text); text = re.sub(r"\s+", " ", text)
    heads = re.findall(r"<h[123][^>]*>(.*?)</h[123]>", html, re.S)
    heads = [re.sub(r"<[^>]+>", "", h).strip() for h in heads]
    qheads = [h for h in heads if re.match(r"(?i)(how|what|why|when|where|who|which|can|should|do|does|is|are)\b", h) or "?" in h]
    out.update({
        "ld_types": sorted(set(ld_types))[:12],
        "has_org": any(t in ("Organization","LocalBusiness","Winery","Store","ProfessionalService") for t in ld_types),
        "has_faq": "FAQPage" in ld_types,
        "title": (re.search(r"<title[^>]*>(.*?)</title>", html, re.S) or [None,""])[1].strip()[:80],
        "meta_desc_len": len((re.search(r'name="description"[^>]*content="([^"]*)"', html) or [None,""])[1]),
        "h1": next(iter(re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)), "NONE")[:70],
        "n_heads": len(heads), "n_qheads": len(qheads),
        "text_chars": len(text),
        "imgs": len(re.findall(r"<img", hl)), "imgs_no_alt": len(re.findall(r"<img(?![^>]*alt=)", hl)),
        "og": 'property="og:' in hl, "noindex": bool(re.search(r'name="robots"[^>]*noindex', hl)),
        "nosnippet": bool(re.search(r'name="robots"[^>]*(nosnippet|max-snippet\s*:\s*0)', hl)),
        "canonical": 'rel="canonical"' in hl,
        "price": bool(re.search(r"\$\s?\d{1,5}", text)),
        "tel": "tel:" in hl, "mailto": "mailto:" in hl,
        "socials": sorted(set(re.findall(r"(facebook|instagram|youtube|linkedin|twitter|tiktok|yelp|tripadvisor)\.", hl)))[:8],
        "booking": bool(re.search(r"book|reserve|reservation|shop|cart|buy|order|tock|opentable|commerce7|vinespring", hl)),
    })
    for p in ["robots.txt", "llms.txt", "sitemap.xml"]:
        s2, b2 = get(site + "/" + p, 12)
        out[p] = {"status": s2, "len": len(b2) if s2 else 0}
        if p == "robots.txt" and s2 == 200:
            bots = ["GPTBot","OAI-SearchBot","ClaudeBot","PerplexityBot","Google-Extended","Meta-ExternalAgent","Applebot-Extended","Amazonbot","CCBot","Bytespider"]
            dis = [b for b in bots if re.search(rf"(?is)user-agent:\s*{b}.*?disallow:\s*/\s*$", b2, re.M)]
            out["blocked_bots"] = dis
        if p == "sitemap.xml" and s2 == 200:
            out["sitemap_valid"] = bool(re.search(r"<(urlset|sitemapindex)", b2))
    # one likely interior page
    links = re.findall(r'href="([^"]+)"', html)
    cand = [l for l in links if re.search(r"(shop|wines|store|visit|tasting|about|contact)", l, re.I) and not l.startswith("http") or (l.startswith(site))]
    if cand:
        u = cand[0] if cand[0].startswith("http") else site + "/" + cand[0].lstrip("/")
        s3, b3 = get(u, 12)
        out["interior"] = {"url": u[:60], "status": s3, "price": bool(re.search(r"\$\s?\d", b3))}
print(json.dumps(out, indent=1))
