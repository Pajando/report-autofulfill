import re, json, urllib.request
req = urllib.request.Request("https://vinosunidos.com/", headers={"User-Agent": "Mozilla/5.0 (Macintosh) Chrome/126"})
h = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
title = (re.search(r"<title[^>]*>(.*?)</title>", h, re.S) or [None, ""])[1].strip()
social_hrefs = sorted(set(re.findall(r'href="(https?://[^"]*(?:facebook|instagram|youtube|linkedin|twitter|x\.com|tiktok|yelp|tripadvisor)[^"]*)"', h, re.I)))[:8]
social_anywhere = sorted(set(re.findall(r'(facebook|instagram|youtube|twitter)\.com/[A-Za-z0-9_.\-]+', h, re.I)))[:8]
print(json.dumps({"title": title[:70], "social_hrefs": social_hrefs, "social_urls_anywhere": social_anywhere}))
