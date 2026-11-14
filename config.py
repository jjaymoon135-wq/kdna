# ==========================================================================
#  KOREA CRE RADAR  —  CONFIG
#  This is the ONE file you edit to tune what the radar catches.
#  After editing, commit the change — the next morning's run uses it.
# ==========================================================================

# --------------------------------------------------------------------------
# 1) SEARCH QUERIES  (each string = its own Google News search)
# --------------------------------------------------------------------------
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
    "반도체 스타트업 투자 유치",
    "팹리스 미국 진출",
    "반도체 소부장 미국",
    "AI 스타트업 시리즈 투자",
    "인공지능 기업 미국 진출",
    "AI 반도체 스타트업",
    "로봇 스타트업 투자 유치",
    "로보틱스 투자",
    "딥테크 스타트업 투자",
    "스타트업 실리콘밸리 진출",
]

QUERIES_EN = [
    "Korean company US expansion",
    "South Korea US factory investment",
    "Korean semiconductor supplier United States",
    "Korean battery plant US",
    "Korean startup raises funding",
    "Korean company IPO Nasdaq",
    "Samsung supplier US site",
    "Hyundai supplier US plant",
    "Korean semiconductor startup funding",
    "Korean fabless chip company US",
    "Korean chip equipment company US expansion",
    "Korean AI startup Series funding",
    "Korean AI chip startup",
    "Korean robotics startup funding",
    "Korean robotics company US expansion",
    "Korean autonomous driving startup US",
    "Korean startup Silicon Valley",
]

# ---- SECONDARY sectors (kept, shown lower & de-emphasized) ----
QUERIES_SECONDARY_KO = [
    "K뷰티 미국 진출",
    "화장품 브랜드 미국 진출",
    "바이오 기업 미국 FDA",
    "바이오텍 나스닥 상장",
    "핀테크 스타트업 투자 유치",
    "소비재 스타트업 미국 진출",
]
QUERIES_SECONDARY_EN = [
    "Korean beauty brand US expansion",
    "K-beauty US launch",
    "Korean biotech FDA US",
    "Korean biotech NASDAQ IPO",
    "Korean fintech startup funding",
    "Korean consumer brand US expansion",
]

# --------------------------------------------------------------------------
# 2) EXCLUDE -- big chaebol you already serve (dropped from results).
#    NOTE: you removed LG and the second-tier chaebol (POSCO, Lotte, etc.).
#    If you want LG excluded too, add "LG", "엘지" back to this list.
# --------------------------------------------------------------------------
EXCLUDE_COMPANIES = [
    "Samsung", "삼성",
    "SK hynix", "SK하이닉스", "SK",
    "Hyundai", "현대", "Kia", "기아",
    "Hanwha", "한화",
]

# --------------------------------------------------------------------------
# 2a) FOREIGN BLOCKLIST -- non-Korean companies that keep slipping through
#     because Korean media covers them. Add any foreign (US/Chinese/Japanese/
#     etc.) company name here the moment you spot it in your feed, and it will
#     be hard-dropped. The AI already tries to exclude foreign companies; this
#     is your manual backstop for stubborn repeat offenders.
# --------------------------------------------------------------------------
FOREIGN_BLOCKLIST = [
    "Positron AI", "Positron",
    "Vecna Robotics", "Vecna",
    "Lightfield",
    "Antioch",
    "Path Robotics",      # Ohio welding-AI firm; Naver Ventures invested
    "Nauticus", "Nauticus Robotics",   # Houston subsea robotics, Nasdaq-listed
]

# --------------------------------------------------------------------------
# 2b) WATCHLIST -- specific companies tracked BY NAME.
#     Each becomes its own search AND gets starred + floated to the top of
#     its section when it appears.
# --------------------------------------------------------------------------
WATCHLIST = [
    "DeepX", "Rainbow Robotics", "Daeduck Electronics", "대덕전자",
    "Fadu Technology", "LX Semicon", "LS Electric", "파두", "HyperAccel",
    "Dongjin Semichem", "동진쎄미켐", "Marqvision", "Mobilint", "모빌린트",
    "Point2 Technology", "XL8", "Openedges", "Neuromeka", "뉴로메카",
    "Bear Robotics", "베어 로보틱스", "VESSL AI", "SEMIFIVE", "Panmnesia",
    "Bitsensing", "Asicland", "에이직랜드", "DeepBrain", "Nota AI",
    "WIRobotics", "Xpanner", "MakinaRocks", "HL Mando", "Chips & Media",
    "SFA Semicon", "ABOV Semiconductor", "Nepes", "네페스", "Alphachips",
    "SEMES", "EUGENETECH", "유진테크", "STRADVISION", "Mangoboost",
    "Hanmi Semiconductor", "한미반도체", "Megazonecloud", "메가존클라우드",
    "Mobiltech US", "Zenix Robotics", "Lablup", "FriendliAI", "Phyxup",
    "CLIKA", "Sendbird", "QueryPie", "Deft Robotics", "SUPERB AI",
    "Contoro Robotics", "Magnachip Semiconductor", "Upstage AI", "Alteogen",
    "Intellian Technology", "Robotis", "Wrtn", "뤼튼", "Park Systems", "파크시스템스",
    "서울반도체", "Seoul Semiconductor", "Primemas", 
    "Neosem Technology", "네오셈", "ITM Semiconductor", "AUROS Technology",
    "BCnC", "DB Hitek", "Eo Technics", "Gaonchips", "HPSP", "Intekplus",
    "Pemtron", "Techwing", "Telechips", "UNITEST",
]

# --------------------------------------------------------------------------
# 2c) WATCHLIST ALIASES -- other spellings (mostly Korean) that should earn a
#     ★ for the company. Used ONLY to recognise a company in a headline; they do
#     not trigger extra searches, so they cost nothing. Spaces are ignored, so
#     "베어 로보틱스" and "베어로보틱스" are the same. These Korean spellings were
#     added from memory: a wrong one only means a missed ★, never a wrong result.
#     Add the Korean name here whenever a watchlist company shows up unstarred.
# --------------------------------------------------------------------------
WATCHLIST_ALIASES = {
    "DeepX": ["딥엑스"],
    "Rainbow Robotics": ["레인보우로보틱스"],
    "HyperAccel": ["하이퍼엑셀"],
    "Panmnesia": ["파네시아"],
    "SEMIFIVE": ["세미파이브"],
    "VESSL AI": ["베슬에이아이", "베슬AI"],
    "Lablup": ["래블업"],
    "FriendliAI": ["프렌들리AI", "프렌들리에이아이"],
    "Upstage AI": ["업스테이지"],
    "MakinaRocks": ["마키나락스"],
    "STRADVISION": ["스트라드비젼", "스트라드비전"],
    "Mangoboost": ["망고부스트"],
    "Openedges": ["오픈엣지"],
    "Alphachips": ["알파칩스"],
    "Telechips": ["텔레칩스"],
    "Gaonchips": ["가온칩스"],
    "Chips & Media": ["칩스앤미디어"],
    "HPSP": ["에이치피에스피"],
    "Eo Technics": ["이오테크닉스"],
    "Techwing": ["테크윙"],
    "UNITEST": ["유니테스트"],
    "Pemtron": ["펨트론"],
    "Intekplus": ["인텍플러스"],
    "Intellian Technology": ["인텔리안테크"],
    "Robotis": ["로보티스"],
    "Sendbird": ["센드버드"],
    "QueryPie": ["쿼리파이"],
    "SUPERB AI": ["슈퍼브에이아이", "슈퍼브AI"],
    "Marqvision": ["마크비전"],
    "XL8": ["엑스엘에이트"],
    "DeepBrain": ["딥브레인"],
    "WIRobotics": ["위로보틱스"],
    "Bitsensing": ["비트센싱"],
    "Primemas": ["프라임마스"],
    "DB Hitek": ["DB하이텍"],
    "Magnachip Semiconductor": ["매그나칩"],
    "Alteogen": ["알테오젠"],
    "LX Semicon": ["LX세미콘"],
    "LS Electric": ["LS일렉트릭"],
    "HL Mando": ["HL만도"],
    "SFA Semicon": ["SFA반도체"],
    "SEMES": ["세메스"],
    "BCnC": ["비씨엔씨"],
    "ITM Semiconductor": ["아이티엠반도체"],
    "CLIKA": ["클리카"],
    "Point2 Technology": ["포인트투테크놀로지", "포인트투"],
}

# --------------------------------------------------------------------------
# 3) SECTORS -- priority tiers. AI tags each kept item with one.
#    "primary" = tech focus (top of each section). "secondary" = below divider.
# --------------------------------------------------------------------------
SECTORS = [
    {"key": "semiconductor", "label": "Semiconductor", "priority": "primary"},
    {"key": "ai",            "label": "AI",            "priority": "primary"},
    {"key": "robotics",      "label": "Robotics",      "priority": "primary"},
    {"key": "deeptech",      "label": "Deep Tech",     "priority": "primary"},
    {"key": "beauty",        "label": "Beauty",        "priority": "secondary"},
    {"key": "bio",           "label": "Bio",           "priority": "secondary"},
    {"key": "retail",        "label": "Retail",        "priority": "secondary"},
    {"key": "finance",       "label": "Finance",       "priority": "secondary"},
    {"key": "other",         "label": "Other",         "priority": "secondary"},
]

# --------------------------------------------------------------------------
# 4) SIGNAL CATEGORIES -- how the page is grouped. Order = display order.
# --------------------------------------------------------------------------
CATEGORIES = [
    {"key": "us_expansion", "label": "US Expansion", "emoji": "🇺🇸"},
    {"key": "funding",      "label": "Funding",      "emoji": "💰"},
    {"key": "ipo",          "label": "IPO / Listing","emoji": "📈"},
    {"key": "other",        "label": "Other Notable","emoji": "•"},
]

# --------------------------------------------------------------------------
# 5) TUNING KNOBS
# --------------------------------------------------------------------------
# 72h so Monday's run covers the weekend in Korea. Safe to be long: headlines
# already judged are remembered (docs/judged.json) and never paid for twice.
LOOKBACK_HOURS = 72
# Model that judges headlines. Haiku 5.5 is cheapest. If foreign companies keep
# slipping through, try "claude-sonnet-5-5" (about 20x the price, still cents/day).
CLAUDE_MODEL = "claude-haiku-5-5"
MAX_ITEMS_TO_JUDGE = 400
DISPLAY_TZ = "America/Los_Angeles"

# Story-dedup sensitivity (0-1). Higher = stricter (fewer things treated as
# duplicates). 0.25 collapses the same story reworded across outlets while
# keeping different events about the same company separate. Lower it toward
# 0.20 if you still see dupes; raise it toward 0.30 if distinct stories merge.
DEDUP_SIMILARITY = 0.30
# Dedup threshold for the AI's clean summaries (they're near-identical for the
# same event, so this is higher). Backstop for dupes crossing AI batches.
DEDUP_SIGNAL_SIMILARITY = 0.5

# --------------------------------------------------------------------------
# 6) BROADER INTAKE (optional extra sources — all fail safe if unavailable)
# --------------------------------------------------------------------------
# (a) Extra Korean tech/startup media RSS feeds, queried directly in addition
#     to Google News. Add any feed URL you like; a dead/broken feed is simply
#     skipped, never crashes the run. Leave empty to use Google News only.
NEWS_RSS_FEEDS = [
    "https://platum.kr/feed",
    "https://www.venturesquare.net/feed",
    "https://byline.network/feed/",
    "https://wowtale.net/feed/",
]

# (b) Naver News search (Korea's biggest aggregator — catches domestic outlets
#     Google misses). OFF unless you add two GitHub secrets: NAVER_CLIENT_ID
#     and NAVER_CLIENT_SECRET (free from developers.naver.com). If the secrets
#     aren't set, this is skipped automatically. These queries are used for it.
NAVER_QUERIES = [
    "스타트업 미국 진출",
    "반도체 스타트업 투자",
    "AI 스타트업 시리즈",
    "로봇 스타트업 투자",
    "코스닥 상장 기술",
    "나스닥 상장 스타트업",
]
