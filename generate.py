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
           [(q, "en") for q in config.QUERIES_EN] + \
           [(q, "ko") for q in config.QUERIES_SECONDARY_KO] + \
           [(q, "en") for q in config.QUERIES_SECONDARY_EN]

    # Each watchlist name becomes its own search so we catch it by name.
    # Language is guessed by whether the name contains Hangul.
    for name in getattr(config, "WATCHLIST", []):
        lang = "ko" if re.search(r"[가-힣]", name) else "en"
        jobs.append((f'{name} 미국' if lang == "ko" else f"{name} US", lang))
        jobs.append((name, lang))

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
    sectors = ", ".join(f'"{s["key"]}" ({s["label"]})' for s in config.SECTORS)
    excludes = ", ".join(config.EXCLUDE_COMPANIES)
    foreign = ", ".join(getattr(config, "FOREIGN_BLOCKLIST", []))
    numbered = "\n".join(
        f'{i}. [{it["lang"]}] {it["title"]}' for i, it in enumerate(items)
    )
    return f"""You are a research analyst for a commercial real estate team that \
serves Korean companies expanding into the United States. The team already serves \
the giant conglomerates, so your job is to surface SMALLER, gettable companies — \
mid-market firms and startups — NOT the chaebol.

From the raw headline pool below, KEEP only items that signal one of these about a \
Korean company:
- US expansion / investment / a new site, plant, HQ, R&D center or office in the US
- a funding round (venture funding, Series A/B/C, capital raise)
- an IPO or stock listing (Korea KOSDAQ/KOSPI or US Nasdaq/NYSE)

*** MOST IMPORTANT RULE — THE COMPANY ITSELF MUST BE KOREAN. ***
The SUBJECT company must be founded/headquartered in South Korea. A Korean-LANGUAGE \
article is NOT enough — Korean media constantly covers FOREIGN startups, and those \
must be DROPPED even though the article is in Korean and mentions funding or the US. \
Judge the nationality of the COMPANY, not the language of the article.
- DROP a Korean-language article about a US, Chinese, Japanese, or other foreign \
company (e.g. a US AI startup raising a round, a US robotics firm, a foreign chipmaker) \
— even if it mentions Korea, Korean investors, or the US market.
- Examples of the kind of FOREIGN companies to DROP: Positron AI, Vecna Robotics, \
Lightfield, Antioch, and any other non-Korean firm. These are NOT Korean and must \
never be kept, regardless of the article's language.
- ALWAYS DROP these specific known-foreign companies if they are the subject: {foreign}.
- If you are not confident the subject company is Korean, DROP it. When unsure, exclude.

HARD EXCLUSION — drop any headline that is centrally about these big conglomerates \
or their divisions/subsidiaries: {excludes}. Also drop any other top-tier Korean \
conglomerate (chaebol) even if not named. If a small company is mentioned only as \
a SUPPLIER to one of these, and the small company is the real subject, KEEP it — \
the focus is the smaller company, not the chaebol.

Also discard: general market commentary, opinion pieces, stock-price chatter, \
sports, unrelated politics.

DEDUPLICATE BY STORY, not just by wording. If several headlines report the SAME \
underlying event (same company + same event), keep only ONE — the clearest — and \
drop the rest.

For every item you KEEP, provide:
- "category": exactly one signal category from: {cats}
- "sector": exactly one sector from: {sectors}. Semiconductor, AI, robotics and \
deep tech are the priority; beauty, bio, retail, finance are secondary. Pick the \
best fit; use "other" only if none fit.
- "en": the headline in clear English. If already English, tidy it; if Korean, \
translate it faithfully. Keep real facts, numbers and company names exactly. Add \
nothing not in the headline. Max ~16 words.
- "ko": the same headline in natural Korean (translate if the source is English). \
Max ~25 characters. Keep real facts; add nothing.

Return STRICT JSON only — no prose, no markdown fences. Shape:
{{"items":[{{"i":<original number>,"category":"<category key>",\
"sector":"<sector key>","en":"<clean English headline>",\
"ko":"<자연스러운 한국어 헤드라인>"}}]}}

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
        "max_tokens": 8000,
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
    """Attach AI category, sector, priority + summaries onto original items."""
    by_cat = {c["key"]: [] for c in config.CATEGORIES}
    valid_cats = set(by_cat.keys())
    sector_meta = {s["key"]: s for s in config.SECTORS}
    watch = [w for w in getattr(config, "WATCHLIST", []) if w.strip()]
    for j in judged.get("items", []):
        try:
            idx = int(j["i"])
            cat = j.get("category", "other")
            if cat not in valid_cats:
                cat = "other"
            src = items[idx]
        except (KeyError, ValueError, IndexError):
            continue
        sec_key = j.get("sector", "other")
        sec = sector_meta.get(sec_key, sector_meta["other"])
        blob = f'{src.get("title","")} {j.get("en","")} {j.get("ko","")}'.lower()
        starred = any(w.lower() in blob for w in watch)
        by_cat[cat].append({
            **src,
            "en": (j.get("en") or "").strip(),
            "ko": (j.get("ko") or "").strip(),
            "sector_key": sec["key"],
            "sector_label": sec["label"],
            "priority": sec["priority"],
            "starred": starred,
        })
    return by_cat


# --------------------------------------------------------------------------
# STEP 4 — RENDER
# --------------------------------------------------------------------------
def render_sections(signals):
    """Render a flat list of signals into category sections (tech-first,
    watchlist starred, secondary below a divider). Reused by every tab."""
    by_cat = {c["key"]: [] for c in config.CATEGORIES}
    for s in signals:
        cat = s.get("category", "other")
        if cat not in by_cat:
            cat = "other"
        by_cat[cat].append(s)

    sections = []
    for c in config.CATEGORIES:
        rows = by_cat.get(c["key"], [])
        if not rows:
            continue
        starred = [r for r in rows if r.get("starred")]
        rest = [r for r in rows if not r.get("starred")]
        primary = [r for r in rest if r.get("priority") == "primary"]
        secondary = [r for r in rest if r.get("priority") != "primary"]
        for lst in (starred, primary, secondary):
            lst.sort(key=lambda x: x.get("published") or "", reverse=True)

        inner = "".join(render_card(r) for r in starred)
        inner += "".join(render_card(r) for r in primary)
        if secondary:
            if starred or primary:
                inner += '<div class="divider">other sectors</div>'
            inner += "".join(render_card(r) for r in secondary)

        sections.append(f"""
        <section class="cat">
          <h2><span class="emoji">{c['emoji']}</span>{html.escape(c['label'])}
              <span class="count">{len(rows)}</span></h2>
          <div class="cards">{inner}</div>
        </section>""")
    return "\n".join(sections) if sections else EMPTY_STATE


def month_bucket(item):
    """Return 'YYYY-MM' for an item, by published date (fallback first_seen)."""
    d = item.get("published") or item.get("first_seen") or ""
    try:
        return datetime.fromisoformat(d).strftime("%Y-%m")
    except ValueError:
        return None


def render_html(archive):
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%A, %B %-d, %Y")

    # --- Latest tab: everything first seen on the most recent run date ---
    latest_date = max((a.get("first_seen", "") for a in archive), default="")[:10]
    latest = [a for a in archive if a.get("first_seen", "")[:10] == latest_date]

    # --- Month tabs ---
    months = {}
    for a in archive:
        mk = month_bucket(a)
        if mk:
            months.setdefault(mk, []).append(a)
    month_order = sorted(months.keys(), reverse=True)

    # Build tab buttons + panels
    tabs = ['<button class="tab active" data-panel="latest">Latest</button>']
    panels = [f'<div class="panel active" id="panel-latest">{render_sections(latest)}</div>']
    for mk in month_order:
        label = datetime.strptime(mk, "%Y-%m").strftime("%b %Y")
        pid = "m" + mk.replace("-", "")
        tabs.append(f'<button class="tab" data-panel="{pid}">{html.escape(label)}'
                    f'<span class="tab-count">{len(months[mk])}</span></button>')
        panels.append(f'<div class="panel" id="panel-{pid}">{render_sections(months[mk])}</div>')

    return PAGE.format(
        date=html.escape(date_str),
        latest_count=len(latest),
        total=len(archive),
        generated=now.strftime("%H:%M UTC"),
        tabs="\n".join(tabs),
        panels="\n".join(panels),
    )


def relative_time(iso_str):
    """Turn an ISO timestamp into 'just now' / '3h ago' / 'yesterday' / 'Sep 7'."""
    if not iso_str:
        return ""
    try:
        then = datetime.fromisoformat(iso_str)
    except ValueError:
        return ""
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - then
    secs = delta.total_seconds()
    if secs < 0:
        return "just now"
    mins = secs / 60
    if mins < 60:
        return "just now" if mins < 5 else f"{int(mins)}m ago"
    hours = mins / 60
    if hours < 24:
        return f"{int(hours)}h ago"
    days = hours / 24
    if days < 2:
        return "yesterday"
    if days < 7:
        return f"{int(days)}d ago"
    return then.strftime("%b %-d")


def render_card(r):
    en = html.escape(r.get("en", "") or r.get("title", ""))
    ko = html.escape(r.get("ko", ""))
    title = html.escape(r.get("title", ""))
    source = html.escape(r.get("source", ""))
    link = html.escape(r.get("link", "#"))
    sector = html.escape(r.get("sector_label", ""))
    when = html.escape(relative_time(r.get("published", "")))
    is_secondary = r.get("priority") != "primary"
    cls = "card secondary" if is_secondary else "card"
    badge_cls = "badge muted" if is_secondary else "badge"
    ko_line = f'<div class="ko">{ko}</div>' if ko else ""
    badge = f'<span class="{badge_cls}">{sector}</span>' if sector else ""
    when_el = f'<span class="when">{when}</span>' if when else ""
    star = '<span class="star">★</span>' if r.get("starred") else ""
    card_cls = cls + " starred" if r.get("starred") else cls
    return f"""
      <a class="{card_cls}" href="{link}" target="_blank" rel="noopener">
        <div class="row">{star}{badge}<span class="en">{en}</span></div>
        {ko_line}
        <div class="meta"><span class="src">{source}</span>{when_el}<span class="head">{title}</span></div>
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
  .card.secondary {{ opacity: .72; }}
  .card.secondary:hover {{ opacity: 1; }}
  .card.starred {{ opacity: 1; border-left: 2px solid var(--accent);
    padding-left: 10px; margin-left: -12px; }}
  .star {{ flex: none; color: var(--accent); font-size: 13px;
    transform: translateY(-1px); }}
  .row {{ display: flex; align-items: baseline; gap: 9px; }}
  .badge {{
    flex: none; font-size: 10.5px; font-weight: 600; letter-spacing: .01em;
    color: var(--accent); background: var(--accent-soft);
    padding: 2px 7px; border-radius: 4px; transform: translateY(-1px);
    white-space: nowrap;
  }}
  .badge.muted {{ color: var(--muted); background: transparent;
    border: 1px solid var(--line); }}
  .divider {{
    font-size: 11px; color: var(--muted); letter-spacing: .06em;
    margin: 14px 0 4px; padding-bottom: 4px;
    display: flex; align-items: center; gap: 10px;
  }}
  .divider::after {{ content: ""; flex: 1; height: 1px; background: var(--line); }}
  .en {{ font-size: 16px; font-weight: 500; line-height: 1.35; }}
  .ko {{ font-family:"IBM Plex Sans KR"; font-size: 14px; color: #3f4a49; margin-top: 2px; }}
  .meta {{
    display: flex; gap: 8px; align-items: baseline; margin-top: 6px;
    font-size: 12px; color: var(--muted);
  }}
  .meta .src {{ color: var(--accent); font-weight: 600; white-space: nowrap; }}
  .meta .when {{ white-space: nowrap; }}
  .meta .when::before {{ content: "·"; margin-right: 8px; opacity: .6; }}
  .meta .head {{
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    opacity: .8;
  }}

  .empty {{ text-align: center; padding: 80px 20px; color: var(--muted); }}
  .empty-mark {{ font-family:"Fraunces",serif; font-size: 48px; color: var(--line); }}
  .empty-sub {{ font-size: 13px; }}

  .tabs {{
    display: flex; gap: 4px; flex-wrap: wrap; margin: 18px 0 4px;
    border-bottom: 1px solid var(--line); padding-bottom: 0;
  }}
  .tab {{
    font-family: inherit; font-size: 13px; font-weight: 500; cursor: pointer;
    color: var(--muted); background: none; border: none;
    padding: 7px 12px 9px; border-bottom: 2px solid transparent;
    margin-bottom: -1px; display: inline-flex; align-items: center; gap: 6px;
  }}
  .tab:hover {{ color: var(--ink); }}
  .tab.active {{ color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }}
  .tab-count {{
    font-size: 10.5px; font-weight: 600; color: var(--muted);
    background: var(--accent-soft); padding: 1px 6px; border-radius: 10px;
  }}
  .tab.active .tab-count {{ color: var(--accent); }}
  .panel {{ display: none; }}
  .panel.active {{ display: block; }}

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
        <div class="count">{latest_count} latest</div>
        <div>{date}</div>
      </div>
    </header>
    <nav class="tabs">
    {tabs}
    </nav>
    {panels}
    <footer>
      <span>Generated {generated} · {total} archived · Google News + Claude</span>
      <span>Tune what it catches in <span class="tune">config.py</span></span>
    </footer>
  </div>
  <script>
    document.querySelectorAll('.tab').forEach(function (t) {{
      t.addEventListener('click', function () {{
        var id = t.getAttribute('data-panel');
        document.querySelectorAll('.tab').forEach(function (x) {{ x.classList.remove('active'); }});
        document.querySelectorAll('.panel').forEach(function (x) {{ x.classList.remove('active'); }});
        t.classList.add('active');
        var p = document.getElementById('panel-' + id);
        if (p) p.classList.add('active');
      }});
    }});
  </script>
</body>
</html>"""


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
def process(items):
    """Judge items in chunks so the AI's output never truncates on heavy days,
    then merge every chunk into one categorized result."""
    by_cat = {c["key"]: [] for c in config.CATEGORIES}
    if not items:
        return by_cat
    chunk_size = 50
    n_chunks = (len(items) + chunk_size - 1) // chunk_size
    for ci in range(n_chunks):
        chunk = items[ci * chunk_size:(ci + 1) * chunk_size]
        if n_chunks > 1:
            print(f"  judging chunk {ci + 1}/{n_chunks} ({len(chunk)} items)")
        judged = call_claude(build_prompt(chunk))
        part = enrich(chunk, judged)          # indices are local to this chunk
        for k, v in part.items():
            by_cat[k].extend(v)
    return by_cat


ARCHIVE_PATH = "docs/archive.json"


def signal_key(item):
    """Stable identity for cross-day dedup: URL if present, else title."""
    link = (item.get("link") or "").strip()
    if link:
        return "u:" + link
    return "t:" + normalize(item.get("title", ""))[:80]


def load_archive():
    try:
        with open(ARCHIVE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_archive(archive):
    os.makedirs("docs", exist_ok=True)
    with open(ARCHIVE_PATH, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=1)


def flatten(by_cat):
    """Turn the category dict into a flat list, category stamped on each item."""
    out = []
    for cat_key, rows in by_cat.items():
        for r in rows:
            out.append({**r, "category": cat_key})
    return out


def merge_into_archive(archive, todays, now_iso):
    """Append today's new signals; skip any already stored (by signal_key)."""
    seen = {signal_key(a) for a in archive}
    added = 0
    for s in todays:
        k = signal_key(s)
        if k in seen:
            continue
        archive.append({**s, "first_seen": now_iso})
        seen.add(k)
        added += 1
    return added


def main():
    print("Korea CRE Radar — building today's page")
    raw = fetch_all()
    items = dedup(raw)

    by_cat = process(items)
    todays = flatten(by_cat)
    print(f"  kept {len(todays)} signals after AI filter")

    archive = load_archive()
    added = merge_into_archive(archive, todays, datetime.now(timezone.utc).isoformat())
    print(f"  archive: +{added} new, {len(archive)} total")
    save_archive(archive)

    out_html = render_html(archive)
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(out_html)
    print("  wrote docs/index.html")


if __name__ == "__main__":
    main()
