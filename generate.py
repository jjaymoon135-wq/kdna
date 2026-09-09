#!/usr/bin/env python3
# ==========================================================================
#  KOREA CRE RADAR  —  ENGINE
#  Fetches Korean-company news, has Claude filter + summarize it, and writes
#  a single skimmable webpage (docs/index.html) that GitHub Pages serves.
#
#  You normally never touch this file. Tune config.py instead.
# ==========================================================================

import os
import re
import sys
import json
import html
import time
import urllib.parse
from datetime import datetime, timezone, timedelta

import feedparser
import requests

import config

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

GOOGLE_NEWS = "https://news.google.com/rss/search"


# --------------------------------------------------------------------------
# STEP 1 — FETCH
# --------------------------------------------------------------------------
def google_news_url(query, lang):
    """Build a Google News RSS search URL for one query in one language."""
    q = urllib.parse.quote(query)
    if lang == "ko":
        params = "hl=ko&gl=KR&ceid=KR:ko"
    else:
        params = "hl=en-US&gl=US&ceid=US:en"
    return f"{GOOGLE_NEWS}?q={q}&{params}"


def fetch_all():
    """Run every query, collect raw items. Returns list of dicts."""
    items = []
    jobs = [(q, "ko") for q in config.QUERIES_KO] + \
           [(q, "en") for q in config.QUERIES_EN]

    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.LOOKBACK_HOURS)

    for query, lang in jobs:
        url = google_news_url(query, lang)
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"  ! fetch failed for '{query}' ({lang}): {e}", file=sys.stderr)
            continue

        for entry in feed.entries:
            # published time (fall back to now if missing)
            published = None
            if getattr(entry, "published_parsed", None):
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if published and published < cutoff:
                continue

            source = ""
            if getattr(entry, "source", None) and getattr(entry.source, "title", None):
                source = entry.source.title

            items.append({
                "title": clean_title(entry.get("title", "")),
                "link": entry.get("link", ""),
                "source": source,
                "published": published.isoformat() if published else "",
                "lang": lang,
                "query": query,
            })
        time.sleep(0.4)  # be polite to Google News

    print(f"  fetched {len(items)} raw items")
    return items


def clean_title(t):
    """Google News appends ' - Source' to titles; trim it and unescape."""
    t = html.unescape(t or "").strip()
    # strip trailing ' - Publisher'
    t = re.sub(r"\s+-\s+[^-]+$", "", t) if t.count(" - ") else t
    return t.strip()


# --------------------------------------------------------------------------
# STEP 2 — DEDUP
# --------------------------------------------------------------------------
def normalize(t):
    return re.sub(r"[^\w가-힣]", "", (t or "").lower())


def dedup(items):
    """Drop near-duplicate headlines (same story from many outlets)."""
    seen = set()
    out = []
    for it in items:
        key = normalize(it["title"])[:60]
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(it)
    # newest first, cap the batch size sent to the AI
    out.sort(key=lambda x: x["published"], reverse=True)
    capped = out[: config.MAX_ITEMS_TO_JUDGE]
    print(f"  {len(capped)} items after dedup (from {len(items)})")
    return capped


# --------------------------------------------------------------------------
# STEP 3 — AI FILTER + SUMMARIZE  (one batched call)
# --------------------------------------------------------------------------
def build_prompt(items):
    cats = ", ".join(f'"{c["key"]}" ({c["label"]})' for c in config.CATEGORIES)
    anchors = ", ".join(config.ANCHOR_COMPANIES)
    numbered = "\n".join(
        f'{i}. [{it["lang"]}] {it["title"]}' for i, it in enumerate(items)
    )
    return f"""You are a research analyst for a commercial real estate team that \
serves Korean companies expanding into the United States. Below is today's raw \
news headline pool. Your job is to keep ONLY items that signal one of these \
things about a KOREAN company:
- expansion / investment / a new site, plant, HQ, R&D or office in the US
- a funding round (venture funding, capital raise)
- an IPO or stock listing (Korea or US)
- a tier-1 supplier or ecosystem move tied to a major anchor account

Anchor accounts whose supplier moves matter: {anchors}

Discard anything irrelevant: general market commentary, non-Korean companies, \
opinion, stock-price chatter, duplicates, sports, unrelated politics.

For every item you KEEP, assign exactly one category from: {cats}

Return STRICT JSON only — no prose, no markdown fences. Shape:
{{"items":[{{"i":<original number>,"category":"<category key>",\
"en":"<=14 word English one-line summary","ko":"<=20자 한국어 한 줄 요약"}}]}}

If nothing qualifies, return {{"items":[]}}.

HEADLINES:
{numbered}
"""


def call_claude(prompt):
    if not ANTHROPIC_API_KEY:
        print("  ! no ANTHROPIC_API_KEY set — skipping AI step", file=sys.stderr)
        return {"items": []}

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": config.CLAUDE_MODEL,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        r = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        return parse_json(text)
    except Exception as e:
        print(f"  ! Claude call failed: {e}", file=sys.stderr)
        return {"items": []}


def parse_json(text):
    """Strip any stray fences and parse. Defensive against model quirks."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    # grab the outermost JSON object if there's leading/trailing junk
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        text = m.group(0)
    try:
        return json.loads(text)
    except Exception as e:
        print(f"  ! could not parse AI JSON: {e}", file=sys.stderr)
        return {"items": []}


def enrich(items, judged):
    """Attach AI category + summaries back onto the original items."""
    by_cat = {c["key"]: [] for c in config.CATEGORIES}
    valid_keys = set(by_cat.keys())
    for j in judged.get("items", []):
        try:
            idx = int(j["i"])
            cat = j.get("category", "other")
            if cat not in valid_keys:
                cat = "other"
            src = items[idx]
        except (KeyError, ValueError, IndexError):
            continue
        by_cat[cat].append({
            **src,
            "en": (j.get("en") or "").strip(),
            "ko": (j.get("ko") or "").strip(),
        })
    return by_cat


# --------------------------------------------------------------------------
# STEP 4 — RENDER
# --------------------------------------------------------------------------
def render_html(by_cat):
    now = datetime.now(timezone.utc)
    total = sum(len(v) for v in by_cat.values())
    date_str = now.strftime("%A, %B %-d, %Y")

    sections = []
    for c in config.CATEGORIES:
        rows = by_cat.get(c["key"], [])
        if not rows:
            continue
        cards = "\n".join(render_card(r) for r in rows)
        sections.append(f"""
        <section class="cat">
          <h2><span class="emoji">{c['emoji']}</span>{html.escape(c['label'])}
              <span class="count">{len(rows)}</span></h2>
          <div class="cards">{cards}</div>
        </section>""")

    body = "\n".join(sections) if sections else EMPTY_STATE
    return PAGE.format(
        date=html.escape(date_str),
        total=total,
        generated=now.strftime("%H:%M UTC"),
        body=body,
    )


def render_card(r):
    en = html.escape(r.get("en", "") or r.get("title", ""))
    ko = html.escape(r.get("ko", ""))
    title = html.escape(r.get("title", ""))
    source = html.escape(r.get("source", ""))
    link = html.escape(r.get("link", "#"))
    ko_line = f'<div class="ko">{ko}</div>' if ko else ""
    return f"""
      <a class="card" href="{link}" target="_blank" rel="noopener">
        <div class="en">{en}</div>
        {ko_line}
        <div class="meta"><span class="src">{source}</span><span class="head">{title}</span></div>
      </a>"""


EMPTY_STATE = """
  <div class="empty">
    <div class="empty-mark">—</div>
    <p>No qualifying signals in the last window.</p>
    <p class="empty-sub">The radar ran clean. Check back tomorrow, or widen the queries in config.py.</p>
  </div>"""


# ---- the page shell (design lives here) ----------------------------------
PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Korea CRE Radar</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+KR:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #14181f;
    --paper: #fbfaf7;
    --line: #e4e0d8;
    --muted: #6a6f78;
    --accent: #1f5f5b;      /* deep teal — reads as "signal", not decoration */
    --accent-soft: #eaf1f0;
    --flag: #b23a2e;
  }}
  * {{ box-sizing: border-box; }}
  html {{ -webkit-text-size-adjust: 100%; }}
  body {{
    margin: 0; background: var(--paper); color: var(--ink);
    font-family: "IBM Plex Sans", "IBM Plex Sans KR", system-ui, sans-serif;
    line-height: 1.5;
  }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 32px 20px 80px; }}

  header {{
    display: flex; align-items: baseline; justify-content: space-between;
    flex-wrap: wrap; gap: 8px 16px;
    border-bottom: 2px solid var(--ink); padding-bottom: 14px; margin-bottom: 4px;
  }}
  h1 {{
    font-family: "Fraunces", Georgia, serif; font-weight: 600;
    font-size: 30px; letter-spacing: -0.01em; margin: 0; line-height: 1.05;
  }}
  h1 .sub {{ display:block; font-family:"IBM Plex Sans"; font-weight:400;
    font-size: 13px; color: var(--muted); letter-spacing: 0; margin-top: 4px; }}
  .stamp {{ text-align: right; font-size: 13px; color: var(--muted); }}
  .stamp .count {{ color: var(--ink); font-weight: 600; }}

  .cat {{ margin-top: 34px; }}
  h2 {{
    display: flex; align-items: center; gap: 10px;
    font-family: "Fraunces", serif; font-weight: 600; font-size: 19px;
    margin: 0 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--line);
  }}
  h2 .emoji {{ font-size: 17px; }}
  h2 .count {{
    margin-left: auto; font-family: "IBM Plex Sans"; font-size: 12px;
    font-weight: 600; color: var(--accent); background: var(--accent-soft);
    padding: 2px 9px; border-radius: 20px;
  }}

  .cards {{ display: flex; flex-direction: column; }}
  .card {{
    display: block; text-decoration: none; color: inherit;
    padding: 13px 4px 14px; border-bottom: 1px solid var(--line);
    transition: padding-left .12s ease, background .12s ease;
  }}
  .card:hover {{ background: #fff; padding-left: 10px; }}
  .card:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .en {{ font-size: 16px; font-weight: 500; line-height: 1.35; }}
  .ko {{ font-family:"IBM Plex Sans KR"; font-size: 14px; color: #3f4a49; margin-top: 2px; }}
  .meta {{
    display: flex; gap: 8px; align-items: baseline; margin-top: 6px;
    font-size: 12px; color: var(--muted);
  }}
  .meta .src {{ color: var(--accent); font-weight: 600; white-space: nowrap; }}
  .meta .head {{
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    opacity: .8;
  }}

  .empty {{ text-align: center; padding: 80px 20px; color: var(--muted); }}
  .empty-mark {{ font-family:"Fraunces",serif; font-size: 48px; color: var(--line); }}
  .empty-sub {{ font-size: 13px; }}

  footer {{ margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line);
    font-size: 12px; color: var(--muted); display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; }}
  a.tune {{ color: var(--accent); text-decoration: none; }}
  a.tune:hover {{ text-decoration: underline; }}

  @media (max-width: 480px) {{
    h1 {{ font-size: 25px; }}
    .meta .head {{ display: none; }}
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --ink:#eceae4; --paper:#15171a; --line:#2b2f36; --muted:#9aa0a8;
             --accent:#5fb8b0; --accent-soft:#1c2b2a; --flag:#e0725f; }}
    .card:hover {{ background:#1b1e22; }}
    .ko {{ color:#b9c3c2; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Korea CRE Radar
        <span class="sub">Korean companies → US expansion · funding · listings</span>
      </h1>
      <div class="stamp">
        <div class="count">{total} signals</div>
        <div>{date}</div>
      </div>
    </header>
    {body}
    <footer>
      <span>Generated {generated} · Google News + Claude</span>
      <span>Tune what it catches in <span class="tune">config.py</span></span>
    </footer>
  </div>
</body>
</html>"""


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
def main():
    print("Korea CRE Radar — building today's page")
    raw = fetch_all()
    items = dedup(raw)

    if items:
        prompt = build_prompt(items)
        judged = call_claude(prompt)
        by_cat = enrich(items, judged)
    else:
        by_cat = {c["key"]: [] for c in config.CATEGORIES}

    kept = sum(len(v) for v in by_cat.values())
    print(f"  kept {kept} signals after AI filter")

    out_html = render_html(by_cat)
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(out_html)
    print("  wrote docs/index.html")


if __name__ == "__main__":
    main()
