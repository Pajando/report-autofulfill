#!/usr/bin/env python3
"""Personalized AI Visibility Report generator (Be the Answer).

Edit the CLIENT dict below for each lead, then run:  python3 report_generator.py
Output lands on the Desktop as "AO-Report-<site>.pdf".
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, HRFlowable,
                                KeepTogether, NextPageTemplate)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Wedge

# CLIENT is loaded from a JSON file passed as argv[1] (built by fulfill.py)
import json, sys
CLIENT = json.load(open(sys.argv[1]))

W, H = letter
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(
    f"~/Desktop/AO-Report-{CLIENT['site'].replace('/','')}.pdf")

NAVY = colors.HexColor("#0F1B2D"); INK = colors.HexColor("#1E2A3A")
SLATE = colors.HexColor("#4A5A6E"); TEAL = colors.HexColor("#0E7C66")
TEAL_BRIGHT = colors.HexColor("#22B899")
AMBER = colors.HexColor("#E8A13C"); RED = colors.HexColor("#D95B4A")
PALE = colors.HexColor("#F1F4F2"); LINE = colors.HexColor("#D3DAD6")
LIGHT_TEAL = colors.HexColor("#E7F3F0"); LIGHT_AMBER = colors.HexColor("#FBF1DF")

def band(score):
    return TEAL_BRIGHT if score >= 65 else (AMBER if score >= 40 else RED)

def st(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10.5, leading=15.5, textColor=INK,
                alignment=TA_LEFT, spaceAfter=8)
    base.update(kw); return ParagraphStyle(name, **base)

S = {
    "body": st("body"),
    "small": st("small", fontSize=9, leading=13, textColor=SLATE),
    "h1": st("h1", fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=NAVY, spaceAfter=6),
    "h2": st("h2", fontName="Helvetica-Bold", fontSize=13, leading=16.5, textColor=NAVY,
             spaceBefore=13, spaceAfter=6, keepWithNext=1),
    "kicker": st("kicker", fontName="Helvetica-Bold", fontSize=9.5, textColor=TEAL, spaceAfter=4),
    "cellh": st("cellh", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
                textColor=colors.white, spaceAfter=0),
    "cell": st("cell", fontSize=9.5, leading=13, spaceAfter=0),
    "celld": st("celld", fontSize=9.5, leading=13, textColor=SLATE, spaceAfter=0),
}

def cover_page(cv, doc):
    cv.saveState()
    cv.setFillColor(NAVY); cv.rect(0, 0, W, H, fill=1, stroke=0)
    cv.setFillColor(TEAL_BRIGHT); cv.rect(0, H-0.5*inch, W, 0.5*inch, fill=1, stroke=0)
    cv.setFillColor(colors.HexColor("#7FC7B6")); cv.setFont("Helvetica-Bold", 12)
    cv.drawString(1*inch, H-2.3*inch, "CONFIDENTIAL AO REPORT · ANSWER OPTIMIZATION")
    biz = CLIENT.get("business") or CLIENT["site"]
    size = 38 if cv.stringWidth(biz, "Helvetica-Bold", 38) <= W - 2*inch else 30
    cv.setFillColor(colors.white); cv.setFont("Helvetica-Bold", size)
    cv.drawString(1*inch, H-3.05*inch, biz)
    cv.setFillColor(TEAL_BRIGHT); cv.setFont("Helvetica-Bold", 15)
    cv.drawString(1*inch, H-3.45*inch, CLIENT["site"])
    cv.setFillColor(colors.HexColor("#C9D3E0")); cv.setFont("Helvetica", 13)
    cv.drawString(1*inch, H-3.85*inch, f"Prepared for {CLIENT['contact']} · {CLIENT['date']}")
    # big score
    c = band(CLIENT["score"])
    cv.setFillColor(c); cv.setFont("Helvetica-Bold", 120)
    cv.drawString(1*inch, H-6.1*inch, str(CLIENT["score"]))
    sw = cv.stringWidth(str(CLIENT["score"]), "Helvetica-Bold", 120)
    cv.setFillColor(colors.HexColor("#8A97A8")); cv.setFont("Helvetica-Bold", 26)
    cv.drawString(1*inch + sw + 10, H-6.1*inch, "/ 100")
    cv.setFillColor(c); cv.setFont("Helvetica-Bold", 22)
    cv.drawString(1*inch, H-6.7*inch, CLIENT["grade"].upper())
    cv.setFillColor(colors.HexColor("#C9D3E0")); cv.setFont("Helvetica", 12.5)
    cv.drawString(1*inch, H-7.35*inch, "How visible your business is to ChatGPT, Gemini, Claude, Perplexity,")
    cv.drawString(1*inch, H-7.6*inch, "Google AI Mode, and the AI agents that now book and buy for customers.")
    cv.setFillColor(colors.HexColor("#8A97A8")); cv.setFont("Helvetica", 9.5)
    cv.drawString(1*inch, 0.85*inch, "Prepared by Alejandro Ojeda · Be the Answer — aoaudit.com · Scan data + live AI tests, July 2026")
    cv.restoreState()

def content_page(cv, doc):
    cv.saveState()
    cv.setFillColor(TEAL_BRIGHT); cv.rect(0, H-0.26*inch, W, 0.26*inch, fill=1, stroke=0)
    cv.setStrokeColor(LINE); cv.setLineWidth(0.6)
    cv.line(0.9*inch, 0.62*inch, W-0.9*inch, 0.62*inch)
    cv.setFillColor(SLATE); cv.setFont("Helvetica", 8)
    biz = CLIENT.get("business") or ""
    left = f"AO REPORT — {biz.upper()} · {CLIENT['site'].upper()}" if biz \
           else f"AO REPORT — {CLIENT['site'].upper()}"
    cv.drawString(0.9*inch, 0.44*inch, left)
    cv.drawRightString(W-0.9*inch, 0.44*inch, f"{doc.page}")
    cv.restoreState()

# ---------- charts ----------
def gauge(score, size=150):
    d = Drawing(size, size)
    cx = cy = size/2; r = size/2 - 4
    d.add(Circle(cx, cy, r, fillColor=PALE, strokeColor=None))
    sweep = score * 3.6
    d.add(Wedge(cx, cy, r, 90 - sweep, 90, fillColor=band(score), strokeColor=None))
    d.add(Circle(cx, cy, r-16, fillColor=colors.white, strokeColor=None))
    d.add(String(cx, cy-8, str(score), fontName="Helvetica-Bold", fontSize=34,
                 fillColor=NAVY, textAnchor="middle"))
    d.add(String(cx, cy-24, "of 100", fontName="Helvetica", fontSize=9,
                 fillColor=SLATE, textAnchor="middle"))
    return d

def pillar_bars(pillars, width=430, rowh=34):
    n = len(pillars); h = n*rowh + 18
    d = Drawing(width, h)
    bar_x, bar_w = 92, width - 92 - 46
    y = h - rowh
    thr_x = bar_x + bar_w * 0.65
    for name, pct in pillars.items():
        d.add(String(0, y+8, name, fontName="Helvetica-Bold", fontSize=10.5, fillColor=NAVY))
        d.add(Rect(bar_x, y+4, bar_w, 13, fillColor=PALE, strokeColor=None, rx=6, ry=6))
        d.add(Rect(bar_x, y+4, bar_w*pct/100, 13, fillColor=band(pct), strokeColor=None, rx=6, ry=6))
        d.add(String(bar_x+bar_w+8, y+6, f"{pct}%", fontName="Helvetica-Bold", fontSize=10.5,
                     fillColor=SLATE))
        y -= rowh
    d.add(Line(thr_x, 6, thr_x, h-8, strokeColor=SLATE, strokeWidth=0.8, strokeDashArray=[3,2]))
    d.add(String(thr_x+4, 0, "healthy: 65%+", fontName="Helvetica", fontSize=7.5, fillColor=SLATE))
    return d

def columns(pairs, width=430, height=170, highlight=0):
    d = Drawing(width, height)
    n = len(pairs); colw = 64; gap = (width - n*colw) / (n+1)
    maxv = 100; base = 26
    for i, (label, val) in enumerate(pairs):
        x = gap + i*(colw+gap)
        bh = (height - base - 26) * val / maxv
        col = band(val) if i == highlight else colors.HexColor("#C9D3D0")
        d.add(Rect(x, base, colw, bh, fillColor=col, strokeColor=None, rx=5, ry=5))
        d.add(String(x+colw/2, base+bh+7, str(val), fontName="Helvetica-Bold", fontSize=13,
                     fillColor=NAVY, textAnchor="middle"))
        d.add(String(x+colw/2, base-14, label, fontName="Helvetica", fontSize=8.5,
                     fillColor=SLATE, textAnchor="middle"))
    d.add(Line(gap/2, base-1.5, width-gap/2, base-1.5, strokeColor=LINE, strokeWidth=1))
    return d

# ---------- document ----------
doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=0.9*inch, rightMargin=0.9*inch,
                      topMargin=0.72*inch, bottomMargin=0.85*inch,
                      title=f"AO Report — {CLIENT['site']}", author="Be the Answer")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=cover_page),
                      PageTemplate(id="content", frames=[frame], onPage=content_page)])

E = [NextPageTemplate("content"), Spacer(1,1), PageBreak()]
def P(t, s="body"): E.append(Paragraph(t, S[s]))
def SP(h=8): E.append(Spacer(1,h))
def PB(): E.append(PageBreak())
def RULE(): E.append(HRFlowable(width="100%", thickness=2, color=TEAL_BRIGHT, spaceBefore=2, spaceAfter=12))

def callout(title, body, bg=LIGHT_TEAL, color=TEAL):
    t = Table([[Paragraph(f"<b>{title}</b>", st("ct", fontName="Helvetica-Bold", fontSize=9.5,
                    textColor=color, spaceAfter=2))],
               [Paragraph(body, st("cb", fontSize=9.5, leading=13.5, spaceAfter=0))]],
              colWidths=[6.7*inch])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(0,0),9),("BOTTOMPADDING",(0,-1),(-1,-1),9),
        ("TOPPADDING",(0,1),(0,1),0),("LINEBEFORE",(0,0),(0,-1),3,color)]))
    return KeepTogether([t])

# ===== EXECUTIVE SUMMARY =====
P("EXECUTIVE SUMMARY", "kicker")
P("Where You Stand Today", "h1")
RULE()
summary = Table([[gauge(CLIENT["score"]),
                  Paragraph(f"<b>{CLIENT['grade']}.</b> {CLIENT['verdict']}",
                            st("v", fontSize=10.5, leading=16, spaceAfter=0))]],
                colWidths=[1.85*inch, 4.85*inch])
summary.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                             ("LEFTPADDING",(1,0),(1,0),14)]))
E.append(summary)
SP(10)
P("Your four pillars", "h2")
P("AI companies don't publish a scoring rubric — these four pillars are how we organize the factors "
  "that research shows actually drive AI visibility: <b>Entity</b> (can machines identify and trust "
  "you?), <b>Content</b> (do your pages hand them quotable answers?), <b>Code</b> (is your site "
  "machine-readable?), <b>Agents</b> (could an AI complete a booking?). Every check rolls up into one.", "small")
SP(4)
E.append(pillar_bars(CLIENT["pillars"]))
SP(10)
P("How you compare", "h2")
E.append(columns([("You today", CLIENT["score"]),
                  ("Typical small biz (our estimate)", 38),
                  ("AI-ready threshold", 85)], highlight=0))
SP(6)
E.append(callout("THE HEADLINE",
  f"You're already ahead of the typical small business ({CLIENT['score']} vs ~38) — your technical "
  f"foundation is real. But the AI-ready threshold is 85, and the gap is concentrated in a handful of "
  f"specific, fixable items on the next pages. Fix the five priorities and you clear it."))
PB()

# ===== ENGINE ACCESS =====
P("COVERAGE CHECK", "kicker")
P("Which AI Ecosystems Can Read You", "h1")
RULE()
P("Every AI assistant, answer engine, and agent platform relies on crawlers that must be allowed to "
  "read your site. One blocked line in robots.txt silently removes you from an entire ecosystem's "
  "answers. We checked all ten major ecosystems:")
SP(4)
eng_rows = [[Paragraph("<b>AI ecosystem</b>", S["cellh"]),
             Paragraph("<b>Access</b>", S["cellh"]),
             Paragraph("<b>What it powers</b>", S["cellh"])]]
POWERS = {
    "ChatGPT / OpenAI": "ChatGPT answers, search citations, Instant Checkout shopping",
    "Claude / Anthropic": "Claude answers and research citations",
    "Gemini / Google AI": "Gemini grounding, AI Mode context, Spark agents",
    "Perplexity": "Perplexity answers — the most citation-hungry engine",
    "Meta AI": "Meta AI across WhatsApp, Instagram, Facebook",
    "Apple Intelligence / Siri": "Siri and Apple Intelligence answers",
    "Amazon Alexa+": "Alexa+ voice recommendations",
    "DuckDuckGo AI": "DuckAssist answers",
    "Model training (Common Crawl)": "Training data feeding most future models",
    "ByteDance / Doubao": "TikTok ecosystem AI answers",
}
for eng, open_ in CLIENT["engines"].items():
    eng_rows.append([Paragraph(f"<b>{eng}</b>", S["cell"]),
                     Paragraph(f'<font color="{"#0E7C66" if open_ else "#D95B4A"}"><b>{"OPEN" if open_ else "BLOCKED"}</b></font>', S["cell"]),
                     Paragraph(POWERS.get(eng, ""), S["celld"])])
t = Table(eng_rows, colWidths=[2.0*inch, 0.85*inch, 3.85*inch], repeatRows=1)
style = [("BACKGROUND",(0,0),(-1,0),NAVY),("VALIGN",(0,0),(-1,-1),"TOP"),
         ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
         ("TOPPADDING",(0,0),(-1,-1),5.5),("BOTTOMPADDING",(0,0),(-1,-1),5.5),
         ("LINEBELOW",(0,0),(-1,-2),0.5,LINE)]
for r in range(1, len(eng_rows)):
    if r % 2 == 0: style.append(("BACKGROUND",(0,r),(-1,r),PALE))
t.setStyle(TableStyle(style))
E.append(t)
SP(10)
open_n = sum(1 for v in CLIENT["engines"].values() if v)
E.append(callout("YOUR RESULT",
  f"{open_n} of {len(CLIENT['engines'])} ecosystems can read your site. "
  + ("That's the full board — your robots.txt is doing exactly what it should. The visibility gap is "
     "not access; it's what the machines find once they're inside (next page)."
     if open_n == len(CLIENT["engines"]) else
     "Unblock the flagged crawlers in robots.txt — every blocked engine is an audience you can never reach.")))
SP(6)
E.append(callout("WHY ACCESS ALONE ISN'T ENOUGH",
  "Being readable is step 1 of 4. The full path to being recommended: <b>1) READ</b> — crawlers can "
  "reach your pages (this page) → <b>2) UNDERSTAND</b> — schema and answer-shaped content tell them "
  "exactly what you offer (Code + Content pillars) → <b>3) TRUST</b> — consistent profiles, reviews, and "
  "mentions confirm you're real and good (Entity pillar) → <b>4) TRANSACT</b> — a booking or purchase "
  "path they can complete (Agents pillar). You pass step 1 everywhere; the next pages show exactly "
  "where steps 2–4 break down.", LIGHT_AMBER, AMBER))
PB()

# ===== FULL FINDINGS =====
P("THE DETAIL", "kicker")
P(f"All {len(CLIENT['findings'])} Checks, One by One", "h1")
RULE()
P("AI visibility involves hundreds of small signals; we test the ones with the strongest documented "
  "effect on whether machines cite and recommend a business. Every item marked FIX points to exactly "
  "where its solution lives — the numbered fixes on the next page, or the playbook.", "small")
SP(4)
f_rows = [[Paragraph("<b>Check</b>", S["cellh"]), Paragraph("<b>Result</b>", S["cellh"]),
           Paragraph("<b>What we found</b>", S["cellh"]),
           Paragraph("<b>Solved in</b>", S["cellh"])]]
for label, ok, detail, fixref in CLIENT["findings"]:
    f_rows.append([Paragraph(label, S["cell"]),
                   Paragraph(f'<font color="{"#0E7C66" if ok else "#D95B4A"}"><b>{"PASS" if ok else "FIX"}</b></font>', S["cell"]),
                   Paragraph(detail, S["celld"]),
                   Paragraph(f'<font color="#E8A13C"><b>{fixref}</b></font>' if fixref else "—", S["celld"])])
t = Table(f_rows, colWidths=[2.0*inch, 0.65*inch, 3.15*inch, 0.9*inch], repeatRows=1)
style = [("BACKGROUND",(0,0),(-1,0),NAVY),("VALIGN",(0,0),(-1,-1),"TOP"),
         ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
         ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
         ("LINEBELOW",(0,0),(-1,-2),0.5,LINE)]
for r in range(1, len(f_rows)):
    if r % 2 == 0: style.append(("BACKGROUND",(0,r),(-1,r),PALE))
t.setStyle(TableStyle(style))
E.append(t)
PB()

# ===== FIX ROADMAP =====
P("THE PLAN", "kicker")
P("Your 5 Priority Fixes", "h1")
RULE()
P("Ranked by impact on your score and on real AI recommendations. Impact and effort are rated out of 5 "
  "— notice how much of this is high-impact, low-effort.", "small")
SP(4)
for i, (title, why, how, impact, effort) in enumerate(CLIENT["fixes"], 1):
    dots = lambda n, c: f'<font color="{c}"><b>{"●"*n}</b></font><font color="#D3DAD6"><b>{"●"*(5-n)}</b></font>'
    block = [
        Paragraph(f'<font color="#0E7C66"><b>{i}. {title}</b></font>   '
                  f'<font size="8">impact {dots(impact,"#0E7C66")}  ·  effort {dots(effort,"#E8A13C")}</font>',
                  st(f"fx{i}", fontName="Helvetica-Bold", fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=3)),
        Paragraph(f"<b>Why:</b> {why}", st(f"fw{i}", fontSize=9.5, leading=13.5, leftIndent=16, spaceAfter=2, textColor=SLATE)),
        Paragraph(f"<b>Do this:</b> {how}", st(f"fh{i}", fontSize=9.5, leading=13.5, leftIndent=16, spaceAfter=6)),
    ]
    E.append(KeepTogether(block))
SP(8)
# ---- Google Profile Scorecard ----
gbp_items = [
    ("Claimed & verified", "The profile is claimed and verified by you"),
    ("100% complete", "Every field filled: categories, services, hours, description, photos"),
    ("Active in last 30 days", "A post or update in the last month (quiet profiles lose visibility)"),
    ("Reviews + responses", "Recent reviews, and you reply to them"),
    ("Products / services listed", "Your offerings and prices are on the profile"),
    ("Q&A seeded", "You've posted and answered common questions"),
]
gbp_rows = [[Paragraph("<b>Google Business Profile — your #1 local asset</b>", S["cellh"]),
             Paragraph("<b>Check yours</b>", S["cellh"])]]
for name, desc in gbp_items:
    gbp_rows.append([Paragraph(f"<b>{name}</b><br/><font size='8' color='#4A5A6E'>{desc}</font>",
                     st(f"gbp{name}", fontSize=9.5, leading=12, spaceAfter=0)),
                     Paragraph("(  ) Yes     (  ) No", st(f"gc{name}", fontSize=9.5, spaceAfter=0))])
gt = Table(gbp_rows, colWidths=[5.1*inch, 1.6*inch])
gstyle = [("BACKGROUND",(0,0),(-1,0),NAVY),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
          ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
          ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
          ("LINEBELOW",(0,0),(-1,-2),0.5,LINE)]
for r in range(1,len(gbp_rows)):
    if r%2==0: gstyle.append(("BACKGROUND",(0,r),(-1,r),PALE))
gt.setStyle(TableStyle(gstyle))
E.append(KeepTogether([Paragraph("Your Google Profile scorecard", S["h2"]), Spacer(1,4), gt]))
SP(4)
E.append(callout("WHY THIS GETS ITS OWN SCORECARD",
  "Google Business Profile is the single biggest local ranking factor there is — it feeds Google Maps "
  "AND Gemini's answers directly. Count your Yes answers above: 5–6 is strong, 3–4 has real upside, "
  "0–2 means you're leaving local customers on the table every day. Fixing it is free (Fix #2), and "
  "keeping it optimized every month is the Google Profile Tune-Up on the last page."))
SP(6)
E.append(callout("A 30-DAY RHYTHM THAT WORKS",
  "Week 1: fixes 1–2 (schema + Google Business Profile). Week 2: fixes 3–4 (pricing page + FAQ). "
  "Week 3: fix 5 (review engine) and re-run the live AI tests. Week 4: re-scan at the audit site and "
  "watch the score move. Then keep the habit: one content improvement and one GBP post per week."))
PB()

# ===== PLATFORM PLAYBOOK =====
P("BEYOND YOUR WEBSITE", "kicker")
P("The Platform Playbook: Claim Every AI Surface", "h1")
RULE()
P("Your website is only half the battle. Each AI assistant pulls business data from specific "
  "sources — and most businesses have never claimed them. Every claim below is free. "
  "<b>Don't try to memorize this table</b> — it's a reference. The 90-minute sprint at the end is "
  "the only to-do.")
SP(4)
plat_rows = [[Paragraph("<b>AI surface</b>", S["cellh"]),
              Paragraph("<b>What actually feeds it</b>", S["cellh"]),
              Paragraph("<b>Your move</b>", S["cellh"])]]
PLATFORMS = [
    ("ChatGPT & ChatGPT Search",
     "Bing's index — one large 2026 analysis found ~87% of ChatGPT search citations match Bing's top results — plus OpenAI's own crawler.",
     "Register at <b>bing.com/webmasters</b> (one-click import from Google Search Console), submit your sitemap, and enable <b>IndexNow</b> so new pages index in minutes. Bing rewards exact-match keywords in titles more than Google does."),
    ("Microsoft Copilot",
     "The Bing index + Bing Places business listings.",
     "Claim <b>bingplaces.com</b> — free, and it can sync automatically from your Google Business Profile."),
    ("Google AI Mode / Gemini / AI Overviews",
     "Google's index, your Google Business Profile, and your schema.",
     "Complete your GBP and post 1–2× weekly; verify your site in Search Console; keep schema valid."),
    ("Claude (Anthropic)",
     "Web-wide brand presence (what the model learned) plus live web search via ClaudeBot / Claude-SearchBot.",
     "Keep ClaudeBot allowed, keep your facts in clean HTML and schema, and get discussed on the open web — Claude favors widely-documented businesses. Your llms.txt is also read by Claude-connected agent tools."),
    ("Siri / Apple Intelligence",
     "Apple Maps — the ONLY source Siri checks for local businesses.",
     "Claim <b>Apple Business</b> at business.apple.com (Business Connect merged into it in April 2026): full profile, photos, and action links (book, order)."),
    ("Amazon Alexa+",
     "Primarily Yelp, plus Bing Places and data aggregators.",
     "Claim your free listing at <b>biz.yelp.com</b> and keep hours/services current; leave Amazonbot allowed in robots.txt."),
    ("Meta AI (WhatsApp · Instagram · Facebook)",
     "Your public Facebook and Instagram business pages.",
     "Complete both business profiles — category, hours, services, link — and keep them active."),
    ("Perplexity",
     "Its own live crawler, plus Yelp/TripAdvisor data for local answers.",
     "Keep PerplexityBot allowed, publish fresh dated content, and maintain your review-site listings."),
    ("Grok (X)",
     "The X firehose plus live web search.",
     "Keep an active X business account — on X, being talked about is being known to Grok."),
    ("LinkedIn",
     "Your company page — crawled by every AI engine, ranked highly in Bing (Microsoft owns LinkedIn), and heavily cited in B2B answers.",
     "Complete your company page with the exact same name and description as everywhere else, post monthly, and link it in your schema sameAs. For B2B businesses this is a primary AI citation source."),
    ("Voice assistants & aggregators",
     "Foursquare, Data Axle and similar aggregators quietly feed many assistants and maps.",
     "Keep your name/address/phone <b>identical everywhere</b>; claim the big aggregators once (free) or use a listings service when revenue justifies it."),
    ("Tomorrow's agent rails",
     "Agentic Commerce Protocol (OpenAI/Stripe — Etsy, Shopify, PayPal), Google's commerce protocol, MCP.",
     "If you sell products, platforms like Etsy/Shopify put you on the rails automatically; keep Product schema and your Merchant Center feed clean. Re-check this list quarterly — it will grow."),
]
for name, feeds, move in PLATFORMS:
    plat_rows.append([Paragraph(f"<b>{name}</b>", S["cell"]),
                      Paragraph(feeds, S["celld"]),
                      Paragraph(move, S["celld"])])
t = Table(plat_rows, colWidths=[1.45*inch, 2.15*inch, 3.1*inch], repeatRows=1)
style = [("BACKGROUND",(0,0),(-1,0),NAVY),("VALIGN",(0,0),(-1,-1),"TOP"),
         ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
         ("TOPPADDING",(0,0),(-1,-1),5.5),("BOTTOMPADDING",(0,0),(-1,-1),5.5),
         ("LINEBELOW",(0,0),(-1,-2),0.5,LINE)]
for r in range(1, len(plat_rows)):
    if r % 2 == 0: style.append(("BACKGROUND",(0,r),(-1,r),PALE))
t.setStyle(TableStyle(style))
E.append(t)
SP(8)
E.append(callout("WHAT ABOUT DEEPSEEK, MANUS, MISTRAL, BRAVE LEO, AND WHATEVER LAUNCHES NEXT?",
  "Honest answer: no separate work needed. Smaller and newer AI tools either lean on the big indexes "
  "(Bing, Google, Brave) or browse your site live the way an agent does. If you've done the moves "
  "above — open crawler access, real HTML, valid schema, claimed profiles, published prices — you are "
  "automatically visible to all of them, including tools that don't exist yet. Chase surfaces with "
  "users, not logos.", PALE, SLATE))
SP(6)
E.append(callout("THE 90-MINUTE CLAIM SPRINT",
  "In one sitting: Google Business Profile → Bing Webmaster Tools + IndexNow → Bing Places → "
  "Apple Business → Yelp → LinkedIn company page → Facebook/Instagram business profiles → X account. "
  "All free, identical name/description/hours on every one. Most businesses never get past the first "
  "— finishing the list puts you ahead of roughly 90% of your market on every AI surface at once."))
PB()

# ===== PROJECTION + CTA =====
P("WHAT HAPPENS IF YOU DO IT", "kicker")
P("Your Projected Score", "h1")
RULE()
E.append(columns([("Today", CLIENT["score"]), ("After the 5 fixes", CLIENT["projected"])],
                 width=330, highlight=1))
SP(8)
P(f"Completing the five priority fixes takes {CLIENT['site']} from <b>{CLIENT['score']} "
  f"({CLIENT['grade'].lower()})</b> to a projected <b>{CLIENT['projected']} (agent-ready)</b> — past "
  "the 85 threshold where AI engines can fully see, verify, quote, and transact with your business. "
  "To be straight with you: the score is a projection of the checks you'd clear, not a guarantee of "
  "rankings — how fast mentions follow depends on your market and competition. Practitioners "
  "typically report movement within 4–8 weeks of the fixes going live: retrieval engines like "
  "Perplexity and Google AI Mode react in weeks; assistant knowledge (ChatGPT, Claude) compounds "
  "over months.")
P("Re-measure monthly", "h2")
P("Ask ChatGPT, Gemini, and Perplexity: “best [your category] in [your area]” and “what is "
  f"[{CLIENT['site'].split('.')[0]}]?” — log whether you're mentioned. Re-scan anytime at "
  "<b>aoaudit.com</b> and watch the score climb as you fix.")
SP(8)
E.append(KeepTogether([
  Paragraph("What is the playbook?", S["h2"]),
  Paragraph("<b>Be the Answer: The AI-Search Authority Playbook</b> is our 12-page, step-by-step guide "
    "to everything this report diagnoses — the “how” behind every fix. Inside: copy-paste JSON-LD "
    "schema templates you adapt in minutes, the answer-first page format with before/after examples, "
    "the walkthroughs for claiming every AI surface (Bing Webmaster + IndexNow, Apple Business, Bing "
    "Places, and the rest), the agent-readiness checklist, how to measure your share of AI answers for "
    "free, and the full 30-day sprint calendar. It's the same system this audit is built on, written "
    "for a non-technical owner working a couple of evenings a week.", S["body"]),
  Spacer(1, 4),
  callout("TWO WAYS TO GET THIS DONE",
    "<b>Do it yourself — the Playbook, $39.</b> Every fix in this report, step by step, with the "
    "copy-paste templates. 30-day no-questions refund. Get it now: "
    "<b>aoaudit.gumroad.com/l/playbook</b><br/><br/>"
    "<b>Have it done for you — The Answer, $497.</b> We implement everything in this report: schema "
    "installed and validated, all profiles claimed (Google, Bing, Apple, Yelp), FAQ page live, prices "
    "published, and a before/after re-scan. <b>Every fix implemented and verified, or it's free.</b> "
    "Typical turnaround: about two weeks. "
    "Reply “ANSWER” to claim a spot — limited to a few businesses at a time. "
    "(For scale: a traditional SEO agency runs $3,000–$8,000/month on a contract.)",
    LIGHT_AMBER, colors.HexColor("#B97A1E")),
  Spacer(1, 6),
  callout("KEEP IT WARM — GOOGLE PROFILE TUNE-UP ($149/mo)",
    "Your Google Business Profile is your #1 local asset — it feeds Google Maps AND Gemini's answers, "
    "and profiles that go quiet for 30+ days measurably lose visibility. After you're fixed, we keep it "
    "working every month: fresh posts, review responses, Q&A, category and service tuning, and a monthly "
    "report. $149/mo, no contract, cancel anytime. Reply “TUNEUP” to add it.",
    LIGHT_TEAL, TEAL),
  Spacer(1, 10),
  Paragraph("Report prepared by Alejandro Ojeda · Be the Answer — aoaudit.com · Data: live site scan "
    "+ AI assistant tests, July 2026. Free-tier and platform behaviors change frequently; figures "
    "verified at time of writing.", S["small"]),
]))

doc.build(E)
print("Wrote", OUT)
