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
    "Intellian Technology", "Robotis", "Wrtn", "뤼튼",
]

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
LOOKBACK_HOURS = 36
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
MAX_ITEMS_TO_JUDGE = 300
DISPLAY_TZ = "America/Los_Angeles"
