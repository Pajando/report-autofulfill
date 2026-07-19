#!/usr/bin/env python3
"""Auto-fulfillment robot for the AI Visibility Audit.

Every run: read unseen FormSubmit lead emails from Gmail (IMAP), build the
personalized report PDF from the embedded report_json, email it to the lead
from the same Gmail account (SMTP), and mark the lead email as seen.

Runs on a GitHub Actions cron. Exits cleanly (0) when GMAIL_USER /
GMAIL_APP_PASSWORD secrets are not configured, so the schedule is harmless
until they're added.

Local test (no email involved):  python3 fulfill.py --test sample_lead.json
"""
import os, re, sys, json, html, imaplib, smtplib, subprocess, tempfile, email
from email.message import EmailMessage
from email.header import decode_header
from datetime import date

IMAP_HOST, SMTP_HOST = "imap.gmail.com", "smtp.gmail.com"
LEAD_SUBJECT = "AO Audit lead"
SKIP_DOMAINS = ("example.com", "example.org", "test.com")

VERDICTS = {
    "Agent-ready": "You're ahead of ~99% of businesses. This report shows how to protect the lead — this landscape shifts quarterly.",
    "Visible, with gaps": "AI engines can find your business, but you're losing citations and agent-driven revenue at specific, fixable points. Every gap in this report is fixable — most within a weekend.",
    "Half-invisible": "AI engines can find your website, but they can't confidently identify, quote, or transact with your business. In practice that means when someone asks ChatGPT or Google's AI for a recommendation in your category, the machines skip you for a competitor they can verify. Every gap in this report is fixable — most within a weekend.",
    "Invisible to AI": "Right now, AI engines can't see, verify, or recommend your business — which means every AI answer in your category goes to someone else. The good news: everything in this report is fixable in weeks, with free tools.",
}
ALL_ENGINES = ["ChatGPT / OpenAI", "Claude / Anthropic", "Gemini / Google AI",
               "Perplexity", "Meta AI", "Apple Intelligence / Siri", "Amazon Alexa+",
               "DuckDuckGo AI", "Model training (Common Crawl)", "ByteDance / Doubao"]


def _name_matches(business, returned):
    """Guard against Places fuzzy-matching a different business (e.g. 'Vinos Unidos Napa'
    once returned a 'Vino\'s' in Arkansas). Require real word overlap before trusting."""
    if not business or not returned:
        return False
    import re
    stop = {"the","and","of","a","inc","llc","co","company","winery","vineyards","vineyard","wines","wine","restaurant","cafe","bar"}
    def words(x): return {w for w in re.findall(r"[a-z0-9]+", x.lower()) if len(w) > 2 and w not in stop}
    b, r = words(business), words(returned)
    if not b: return False
    return len(b & r) >= max(1, len(b) // 2)  # at least half the distinctive words must match


def fetch_reputation(business, site, locality=""):
    """Lead-triggered Google rating pull via our worker's /places endpoint.
    Sends a PRECISE query (business + locality) and verifies the returned name
    actually matches before trusting it — Places fuzzy-matches, so a loose query
    can return a stranger. Any error, mismatch, or non-JSON = silently skipped."""
    try:
        import urllib.request, urllib.parse, json as _json
        query = f"{business} {locality}".strip() if business else site
        q = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"https://ao-relay.aojedamedia.workers.dev/places?q={q}",
            headers={"Origin": "https://aoaudit.com"})
        with urllib.request.urlopen(req, timeout=10) as r:
            j = _json.loads(r.read().decode())
        if j.get("rating") and _name_matches(business, j.get("name", "")):
            return j
    except Exception:
        pass
    return None


def build_client(data):
    """Transform the site's report_json into the template's CLIENT dict."""
    score = int(data["score"])
    grade = data.get("grade", "Half-invisible")
    fixes = []
    for fx in data.get("fixes", [])[:5]:
        text = fx["f"]
        parts = text.split(". ", 1)
        why = parts[0].rstrip(".") + "."
        how = parts[1] if len(parts) > 1 else text
        impact = 5 if fx.get("w", 5) >= 6 else 4
        fixes.append((fx["t"], why, how, impact, 2))
    fix_titles = [f[0] for f in fixes]
    findings = []
    for label, status, detail in data.get("findings", []):
        passed = status == "pass"
        det = detail if passed or status == "fail" else "Needs a manual check: " + detail
        ref = ""
        if not passed and label in fix_titles:
            ref = f"Fix #{fix_titles.index(label)+1}"
        elif not passed:
            ref = "Playbook"
        findings.append((label, passed, det, ref))
    blocked = set(data.get("blocked", []))
    return {
        "site": data["site"],
        "business": data.get("business") or data["site"],
        "contact": data.get("name") or "there",
        "date": date.today().strftime("%B %-d, %Y"),
        "score": score,
        "grade": grade,
        "verdict": VERDICTS.get(grade, VERDICTS["Half-invisible"]),
        "pillars": data["pillars"],
        "engines": {e: (e not in blocked) for e in ALL_ENGINES},
        "findings": findings,
        "_reputation": None,
        "fixes": fixes,
        "projected": max(86, min(95, score + 30)) if score < 86 else min(97, score + 4),
    }


def generate_pdf(client):
    here = os.path.dirname(os.path.abspath(__file__))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(client, f)
        cfg = f.name
    out = os.path.join(tempfile.mkdtemp(prefix="fulfill-"),
                       f"AO-Report-{client['site'].replace('/','')}.pdf")
    subprocess.run([sys.executable, os.path.join(here, "report_template.py"), cfg, out],
                   check=True)
    if not os.path.exists(out):
        raise RuntimeError(f"report not produced at {out}")
    return out


def send_report(user, pw, lead_email, client, pdf_path):
    first = (client["contact"] or "there").split()[0]
    biz = client["business"]
    msg = EmailMessage()
    msg["From"] = f"Alejandro Ojeda — Be the Answer <{user}>"
    msg["To"] = lead_email
    msg["Subject"] = f"Your AO Report — {biz} ({client['score']}/100)"
    msg.set_content(f"""Hi {first},

Your full AO Report for {biz} is attached — your AO Score breakdown — every finding from
your scan explained, and your prioritized fix list.

Two ways to get it all done:

1) DO IT YOURSELF — "Be the Answer: The AI-Search Authority Playbook" ($39)
   walks you through every fix step by step, with copy-paste templates.
   Get it here: https://aoaudit.gumroad.com/l/playbook

2) DONE FOR YOU — The Answer ($497): I implement everything in your report
   — schema, profiles, FAQ page, prices — done right, or it's free.
   Typical turnaround: about two weeks. Reply "ANSWER" to claim a spot.

Questions about anything in the report? Just hit reply — a human reads this.

Alejandro
Be the Answer — aoaudit.com
https://aoaudit.com/""")
    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf",
                           filename=f"AO-Report-{biz.replace(' ','-')}.pdf")
    with smtplib.SMTP_SSL(SMTP_HOST, 465) as s:
        s.login(user, pw)
        s.send_message(msg)


def extract_report_json(raw_email):
    m = email.message_from_bytes(raw_email)
    bodies = []
    for part in m.walk():
        if part.get_content_type() in ("text/html", "text/plain"):
            try:
                bodies.append(part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", "replace"))
            except Exception:
                pass
    for body in bodies:
        hit = re.search(r"report_json.*?(\{.*)", body, re.S)
        if not hit:
            continue
        blob = html.unescape(hit.group(1))
        # trim to the balanced JSON object
        depth = 0
        for i, ch in enumerate(blob):
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(blob[:i+1])
                    except json.JSONDecodeError:
                        break
    return None


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--test":
        data = json.load(open(sys.argv[2]))
        client = build_client(data)
        rep = fetch_reputation(client.get("business"), client.get("site"), client.get("locality", ""))
        if rep:
            client["findings"].append((
                "Google rating (live pull, report day)", True,
                f"{rep['rating']}\u2605 \u00b7 {rep['count']} reviews on Google (official Places data, pulled the day this report was built). "
                + ("A strong human-trust signal \u2014 now make the machines see it." if rep["count"] >= 10 else
                   "A thin review base \u2014 the review-engine fix below matters double."), ""))
        pdf = generate_pdf(client)
        print("TEST OK — generated:", pdf)
        return

    user, pw = os.environ.get("GMAIL_USER"), os.environ.get("GMAIL_APP_PASSWORD")
    if not user or not pw:
        print("Secrets not configured yet — nothing to do.")
        return

    box = imaplib.IMAP4_SSL(IMAP_HOST)
    box.login(user, pw)
    box.select("INBOX")
    ok, ids = box.search(None, 'UNSEEN', 'FROM', '"formsubmit.co"',
                         'SUBJECT', f'"{LEAD_SUBJECT}"')
    ids = ids[0].split() if ok == "OK" else []
    print(f"{len(ids)} new lead(s)")
    for num in ids:
        ok, parts = box.fetch(num, "(RFC822)")
        if ok != "OK":
            continue
        data = extract_report_json(parts[0][1])
        if not data:
            print(f"  lead {num.decode()}: no report_json (old-format lead) — leaving for manual handling")
            box.store(num, "+FLAGS", "\\Seen")
            continue
        if data.get("relay_outage"):
            # scan ran during a relay outage — automated findings are missing and the site
            # promised "we'll run your full scan ourselves". Leave UNREAD for the human.
            print(f"  lead {num.decode()}: RELAY OUTAGE during their scan — leaving unread for a manual full scan")
            continue
        lead_email = (data.get("email") or "").strip()
        if not lead_email:
            # email lives in its own field; fall back to parsing the table
            body = parts[0][1].decode("utf-8", "replace")
            m = re.search(r"email</td>\s*<td[^>]*>.*?([\w.+-]+@[\w.-]+\.\w+)", body, re.S | re.I)
            lead_email = m.group(1) if m else ""
        if not lead_email or lead_email.split("@")[-1].lower() in SKIP_DOMAINS:
            print(f"  lead {num.decode()}: no usable email ({lead_email!r}) — skipped")
            box.store(num, "+FLAGS", "\\Seen")
            continue
        try:
            client = build_client(data)
            rep = fetch_reputation(client.get("business"), client.get("site"), client.get("locality", ""))
            if rep:
                client["findings"].append((
                    "Google rating (live pull, report day)", True,
                    f"{rep['rating']}\u2605 \u00b7 {rep['count']} reviews on Google (official Places data, pulled the day this report was built). "
                    + ("A strong human-trust signal \u2014 now make the machines see it." if rep["count"] >= 10 else
                       "A thin review base \u2014 the review-engine fix below matters double."), ""))
            pdf = generate_pdf(client)
            send_report(user, pw, lead_email, client, pdf)
            box.store(num, "+FLAGS", "\\Seen")
            print(f"  sent {client['site']} ({client['score']}/100) -> {lead_email}")
        except Exception as e:
            print(f"  lead {num.decode()}: FAILED — {e} (left unseen for retry)")
    box.logout()


if __name__ == "__main__":
    main()
