import json, urllib.request
req = urllib.request.Request("https://vinosunidos.com/products.json?limit=50",
    headers={"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126"})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    prices = []
    for p in data.get("products", []):
        for v in p.get("variants", []):
            try: prices.append(float(v["price"]))
            except: pass
    prices.sort()
    print(json.dumps({"n_products": len(data.get("products", [])), "n_prices": len(prices),
        "min": prices[0] if prices else None, "max": prices[-1] if prices else None,
        "median": prices[len(prices)//2] if prices else None,
        "sample_titles": [p["title"][:40] for p in data.get("products", [])[:6]]}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
