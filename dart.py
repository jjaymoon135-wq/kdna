# ==========================================================================
#  KOREA CRE RADAR  —  DART LAYER (OpenDART)
#  Verification layer: confirms whether money is actually going to the US.
#  Fully isolated from the news pipeline. Every public function fails safe:
#  on any DART error the caller gets an "unavailable" result and the news
#  page still builds. The API key is read from the env and NEVER logged.
# ==========================================================================

import os
import io
import re
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

import requests

API = "https://opendart.fss.or.kr/api"
VIEWER = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}"

# report_nm keywords to KEEP, mapped to a display category ------------------
REPORT_CATEGORIES = [
    ("신규시설투자",                       "Facility investment"),
    ("타법인주식 및 출자증권 취득",         "Equity acquisition"),
    ("유상증자결정",                       "Paid-in capital increase"),
    ("전환사채권발행결정",                 "Convertible bond"),
    ("신주인수권부사채권발행결정",         "Warrant bond"),
    ("회사채",                             "Corporate bond"),
    ("유형자산 취득",                       "Tangible asset acquisition"),
    ("유형자산 처분",                       "Tangible asset disposal"),
    ("채무보증",                           "Debt guarantee"),
    ("영업양수",                           "Business acquisition"),
    ("자산양수",                           "Asset acquisition"),
    ("증권신고서",                         "Securities registration"),
]
KEEP_KEYWORDS = [k for k, _ in REPORT_CATEGORIES]

# US signal vocabulary ------------------------------------------------------
US_STATES = [
    "Texas", "텍사스", "California", "캘리포니아", "Georgia", "조지아",
    "Arizona", "애리조나", "Ohio", "오하이오", "Michigan", "미시간",
    "Tennessee", "테네시", "Indiana", "인디애나", "New York", "뉴욕",
    "Nevada", "네바다", "North Carolina", "노스캐롤라이나", "Virginia", "버지니아",
    "Alabama", "앨라배마", "Kentucky", "켄터키", "New Jersey", "뉴저지",
]
US_CITIES = [
    "Taylor", "테일러", "Austin", "오스틴", "Fremont", "프리몬트",
    "San Jose", "새너제이", "산호세", "Santa Clara", "산타클라라",
    "Silicon Valley", "실리콘밸리", "Sunnyvale", "서니베일",
    "Palo Alto", "팔로알토", "Atlanta", "애틀랜타", "Phoenix", "피닉스",
    "Detroit", "디트로이트", "Savannah", "서배너", "Ellabell",
]
US_GENERIC = ["미국", "U.S.", "U.S.A", "USA", "United States", "Inc.", "LLC", "Corp.", " Co."]
# things that mean the money is going somewhere else (NOT a US trigger)
NON_US_HINTS = [
    "베트남", "Vietnam", "인도", "India", "인도네시아", "Indonesia",
    "헝가리", "Hungary", "폴란드", "Poland", "중국", "China", "우즈베키스탄",
    "Uzbekistan", "말레이시아", "Malaysia", "태국", "Thailand", "유럽", "Europe",
    "일본", "Japan", "멕시코", "Mexico", "국내", "충청", "경기도", "전라",
]


def _dart_key():
    return os.environ.get("DART_API_KEY", "")


def _get(path, params, timeout=30):
    """GET a DART endpoint. Returns requests.Response or raises."""
    params = dict(params)
    params["crtfc_key"] = _dart_key()
    r = requests.get(f"{API}/{path}", params=params, timeout=timeout)
    r.raise_for_status()
    return r


# --------------------------------------------------------------------------
# STEP 1 — list filings, filter, dedupe amendments
# --------------------------------------------------------------------------
def fetch_filings(days=3):
    """Return kept filings from the last `days` days for pblntf_ty B and C.
    Raises on hard DART failure so the caller can mark DART unavailable."""
    if not _dart_key():
        raise RuntimeError("DART_API_KEY not set")

    end = datetime.now(timezone.utc)
    bgn = end - timedelta(days=days)
    bgn_de, end_de = bgn.strftime("%Y%m%d"), end.strftime("%Y%m%d")

    raw = []
    for ty in ("B", "C"):
        page = 1
        while True:
            resp = _get("list.json", {
                "bgn_de": bgn_de, "end_de": end_de,
                "pblntf_ty": ty, "page_no": page, "page_count": 100,
            }).json()
            status = resp.get("status")
            if status == "013":            # no data for this type/window
                break
            if status == "020":            # rate limited — bubble up
                raise RuntimeError("DART rate limit (020)")
            if status != "000":
                raise RuntimeError(f"DART status {status}: {resp.get('message')}")
            raw.extend(resp.get("list", []))
            total_page = int(resp.get("total_page", 1) or 1)
            if page >= total_page:
                break
            page += 1

    kept = [f for f in raw if any(k in (f.get("report_nm") or "") for k in KEEP_KEYWORDS)]
    return dedupe_amendments(kept)


def categorize(report_nm):
    for kw, label in REPORT_CATEGORIES:
        if kw in (report_nm or ""):
            return label
    return "Other filing"


def _base_title(report_nm):
    """Strip the [기재정정] / [첨부정정] amendment prefix and brackets."""
    return re.sub(r"\[[^\]]*\]", "", report_nm or "").strip()


def dedupe_amendments(filings):
    """Same event refiled as [기재정정] should appear once. Key on
    company + base title; keep the newest receipt (latest rcept_no)."""
    best = {}
    for f in filings:
        key = (f.get("corp_code"), _base_title(f.get("report_nm")))
        cur = best.get(key)
        if cur is None or (f.get("rcept_no") or "") > (cur.get("rcept_no") or ""):
            best[key] = f
    # newest first
    return sorted(best.values(), key=lambda x: x.get("rcept_no", ""), reverse=True)


# --------------------------------------------------------------------------
# STEP 2 — US relevance
# --------------------------------------------------------------------------
def _fetch_body_text(rcept_no):
    """Download document.xml (a ZIP), return concatenated text of the XML
    documents inside. Returns None if it can't be fetched/parsed."""
    try:
        r = _get("document.xml", {"rcept_no": rcept_no}, timeout=40)
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        chunks = []
        for name in zf.namelist():
            data = zf.read(name)
            for enc in ("utf-8", "euc-kr", "cp949"):
                try:
                    chunks.append(data.decode(enc))
                    break
                except UnicodeDecodeError:
                    continue
        text = "\n".join(chunks)
        # strip XML/HTML tags to plain text
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text or None
    except Exception as e:
        print(f"  ! dart body fetch failed ({rcept_no}): {type(e).__name__}", file=sys.stderr)
        return None


def score_us_relevance(body_text):
    """Return (tag, matched_signals). tag in US-confirmed / Unclear / Non-US.
    body_text None -> Unclear (never guess)."""
    if not body_text:
        return "unclear", []
    hits = []
    for term in US_STATES + US_CITIES + US_GENERIC:
        if term and term in body_text:
            hits.append(term.strip())
    non_us = [t for t in NON_US_HINTS if t and t in body_text]

    # strong US signal = a state or city name (specific location)
    strong = [h for h in hits if h in {s.strip() for s in US_STATES + US_CITIES}]
    if strong:
        return "us", sorted(set(hits))[:8]
    if hits and not non_us:
        return "us", sorted(set(hits))[:8]     # generic US words, no other-region noise
    if non_us and not strong:
        return "nonus", sorted(set(non_us))[:6]
    if hits:
        return "unclear", sorted(set(hits))[:8]
    return "unclear", []


# --------------------------------------------------------------------------
# STEP 3 — corp_code cache (for name<->code; monthly refresh)
# --------------------------------------------------------------------------
def load_corpcode(cache_path, max_age_days=30):
    """Return {corp_name: corp_code}. Cached to cache_path; refreshed monthly.
    Fails soft: returns {} if it can't be built."""
    try:
        with open(cache_path, encoding="utf-8") as fh:
            blob = json.load(fh)
        ts = datetime.fromisoformat(blob.get("fetched_at"))
        if datetime.now(timezone.utc) - ts < timedelta(days=max_age_days):
            return blob.get("map", {})
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        pass
    # (re)download
    try:
        r = _get("corpCode.xml", {}, timeout=60)
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        xml_bytes = zf.read(zf.namelist()[0])
        root = ET.fromstring(xml_bytes)
        m = {}
        for el in root.iter("list"):
            name = (el.findtext("corp_name") or "").strip()
            code = (el.findtext("corp_code") or "").strip()
            if name and code:
                m[name] = code
        with open(cache_path, "w", encoding="utf-8") as fh:
            json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(), "map": m},
                      fh, ensure_ascii=False)
        return m
    except Exception as e:
        print(f"  ! corpCode load failed: {type(e).__name__}", file=sys.stderr)
        return {}


# --------------------------------------------------------------------------
# ORCHESTRATION
# --------------------------------------------------------------------------
def build_dart_layer(cache_path, days=3, max_body_fetches=120):
    """Full DART layer. Returns dict with filings (each scored) + meta.
    Raises only on total failure (so caller marks unavailable); per-filing
    body errors degrade to 'unclear'."""
    cache = _load_cache(cache_path)
    filings = fetch_filings(days=days)

    out = []
    fetches = 0
    for f in filings:
        rcept = f.get("rcept_no", "")
        rec = {
            "corp_name": f.get("corp_name", ""),
            "corp_code": f.get("corp_code", ""),
            "report_nm": f.get("report_nm", ""),
            "category": categorize(f.get("report_nm", "")),
            "rcept_no": rcept,
            "rcept_dt": f.get("rcept_dt", ""),
            "corp_cls": f.get("corp_cls", ""),
            "link": VIEWER.format(rcept),
        }
        cached = cache.get(rcept)
        if cached:                                   # already scored — reuse
            rec["us_tag"] = cached["us_tag"]
            rec["us_signals"] = cached.get("us_signals", [])
        elif fetches < max_body_fetches:             # fetch + score once
            body = _fetch_body_text(rcept)
            tag, sig = score_us_relevance(body)
            rec["us_tag"], rec["us_signals"] = tag, sig
            cache[rcept] = {"us_tag": tag, "us_signals": sig,
                            "scored_at": datetime.now(timezone.utc).isoformat()}
            fetches += 1
        else:                                        # over budget this run
            rec["us_tag"], rec["us_signals"] = "unclear", []
        out.append(rec)

    _save_cache(cache_path, cache)
    return {"filings": out, "fetched_bodies": fetches, "count": len(out)}


def _load_cache(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_cache(path, cache):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, ensure_ascii=False)
    except OSError:
        pass


# --------------------------------------------------------------------------
# CROSS-SIGNAL  (news company also in a DART filing within N days -> 🔥)
# --------------------------------------------------------------------------
def _norm_name(s):
    """Loose normalize a company name for matching (drop suffixes/spaces)."""
    s = re.sub(r"\((주|유|재)\)|주식회사|㈜|Inc\.?|Corp\.?|Co\.?|Ltd\.?|LLC", "", s or "")
    return re.sub(r"[\s,\.]", "", s).lower()


def find_double_signals(dart_filings, news_items, days=14):
    """A company in BOTH a DART filing and a recent news item (within `days`)
    gets 🔥. Matches DART corp_name against news title/summary text.
    Returns (set_of_flagged_corp_names, list_of_top_signal_rows)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent_news = []
    for n in news_items:
        p = n.get("published") or n.get("first_seen") or ""
        try:
            if datetime.fromisoformat(p) < cutoff:
                continue
        except ValueError:
            pass
        blob = f'{n.get("title","")} {n.get("en","")} {n.get("ko","")}'
        recent_news.append((blob, _norm_name_blob(blob), n))

    flagged, tops = set(), []
    for f in dart_filings:
        cn = f.get("corp_name", "")
        if not cn:
            continue
        key = _norm_name(cn)
        if len(key) < 2:
            continue
        match = None
        for blob, nblob, n in recent_news:
            if cn in blob or key in nblob:
                match = n
                break
        if match:
            flagged.add(cn)
            tops.append({"filing": f, "news": match})
    return flagged, tops


def _norm_name_blob(blob):
    return re.sub(r"[\s,\.]", "", blob or "").lower()
