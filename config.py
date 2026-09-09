# ==========================================================================
#  KOREA CRE RADAR  —  CONFIG
#  This is the ONE file you edit to tune what the radar catches.
#  Everything below is a plain list. Add / remove / reword lines freely.
#  After editing, commit the change — the next morning's run uses it.
# ==========================================================================

# --------------------------------------------------------------------------
# 1) SEARCH QUERIES
#    Each string is run as its own Google News search (Korean + English).
#    Keep them specific enough to avoid noise, broad enough to catch signal.
#    Tip: after a week, look at what got through and what didn't, and tune here.
# --------------------------------------------------------------------------

# Korean-language queries (searched on Korean Google News)
QUERIES_KO = [
    "한국 기업 미국 진출",
    "한국 기업 미국 공장",
    "미국 현지 법인 설립",
    "미국 투자 발표 한국",
    "반도체 협력사 미국",
    "배터리 공장 미국 투자",
    "미국 생산기지",
    "스타트업 투자 유치 시리즈",
    "코스닥 상장 예비심사",
    "나스닥 상장 한국",
    "미국 IPO 한국 기업",
]

# English-language queries (searched on US Google News)
QUERIES_EN = [
    "Korean company US expansion",
    "South Korea US factory investment",
    "Korean semiconductor supplier United States",
    "Korean battery plant US",
    "Korean startup raises funding",
    "Korean company IPO Nasdaq",
    "Samsung supplier US site",
    "Hyundai supplier US plant",
]

# --------------------------------------------------------------------------
# 2) ANCHOR COMPANIES
#    When these move, their tier-1 suppliers follow — the gettable clients.
#    Listed so the AI knows to flag supplier/ecosystem moves around them.
#    (Add or trim to match the accounts your team actually tracks.)
# --------------------------------------------------------------------------
ANCHOR_COMPANIES = [
    "Samsung Electronics", "Samsung SDI", "Samsung SDS",
    "SK hynix", "SK On", "SK Siltron",
    "Hyundai Motor", "Kia", "Hyundai Mobis",
    "LG Energy Solution", "LG Chem", "LG Electronics",
    "POSCO", "Hanwha", "Doosan",
]

# --------------------------------------------------------------------------
# 3) CATEGORIES
#    How each item gets bucketed on the page. Order = display order.
#    key must be unique; label is what you see; emoji is decoration.
# --------------------------------------------------------------------------
CATEGORIES = [
    {"key": "us_expansion", "label": "US Expansion",        "emoji": "🇺🇸"},
    {"key": "funding",      "label": "Funding",             "emoji": "💰"},
    {"key": "ipo",          "label": "IPO / Listing",       "emoji": "📈"},
    {"key": "supplier",     "label": "Supplier / Ecosystem","emoji": "🔗"},
    {"key": "other",        "label": "Other Notable",       "emoji": "•"},
]

# --------------------------------------------------------------------------
# 4) TUNING KNOBS
# --------------------------------------------------------------------------
# How many hours back to look. Runs daily; 36h gives overlap so nothing
# slips through the cracks between runs. Dedup handles the overlap.
LOOKBACK_HOURS = 36

# The Claude model used for filtering + summarizing. Haiku is cheapest and
# more than good enough for this. Change only if you have a reason to.
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Max headlines sent to the AI in one batch. Keeps cost + context sane.
MAX_ITEMS_TO_JUDGE = 180

# Timezone label shown on the page (display only — schedule is set in the
# GitHub Actions workflow file).
DISPLAY_TZ = "America/Los_Angeles"
