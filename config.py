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


# --------------------------------------------------------------------------
# 1b) MARKETS -- the metros you cover. Each one adds two searches (English +
#     Korean) and a tag on every story that mentions it (shown as a chip and
#     usable as a filter on the page). "terms" are matched against the headline
#     ignoring case, spaces and dashes. Add a market by copying a block.
#     Avoid bare "georgia" (it is also the country) and bare "la".
# --------------------------------------------------------------------------
MARKETS = [
    {"key": "LA",  "label": "LA",
     "q_en": "Korean company Los Angeles", "q_ko": "한국 기업 로스앤젤레스",
     "terms": ["los angeles", "koreatown", "로스앤젤레스", "엘에이", "한인타운", "vernon", "gardena", "torrance", "city of industry"]},
    {"key": "OC",  "label": "OC",
     "q_en": "Korean company Orange County California Irvine", "q_ko": "한국 기업 오렌지카운티 어바인",
     "terms": ["orange county", "irvine", "anaheim", "buena park", "fullerton", "오렌지카운티", "어바인", "애너하임", "부에나파크"]},
    {"key": "SV",  "label": "SV",
     "q_en": "Korean company Silicon Valley San Jose Santa Clara", "q_ko": "한국 기업 실리콘밸리 산호세",
     "terms": ["silicon valley", "san jose", "santa clara", "sunnyvale", "fremont", "milpitas", "palo alto", "mountain view", "bay area", "실리콘밸리", "산호세", "산타클라라", "서니베일", "프리몬트", "베이에어리어"]},
    {"key": "DAL", "label": "DAL",
     "q_en": "Korean company Dallas Plano Frisco Texas", "q_ko": "한국 기업 댈러스 플레이노",
     "terms": ["dallas", "plano", "frisco", "carrollton", "fort worth", "richardson", "allen, tx", "댈러스", "플레이노", "프리스코", "캐롤턴", "포트워스"]},
    {"key": "HOU", "label": "HOU",
     "q_en": "Korean company Houston Texas", "q_ko": "한국 기업 휴스턴",
     "terms": ["houston", "katy", "sugar land", "휴스턴", "슈거랜드"]},
    {"key": "ATX", "label": "ATX",
     "q_en": "Korean company Austin Taylor Texas Samsung", "q_ko": "한국 기업 오스틴 테일러 텍사스",
     "terms": ["austin", "round rock", "pflugerville", "taylor fab", "taylor, texas", "taylor texas", "오스틴", "라운드록", "테일러 공장", "테일러시", "테일러 팹"]},
    {"key": "ATL", "label": "ATL",
     "q_en": "Korean company Atlanta Georgia plant", "q_ko": "한국 기업 애틀랜타 조지아주",
     "terms": ["atlanta", "savannah", "gwinnett", "duluth, ga", "metaplant", "bryan county", "lagrange", "cartersville", "애틀랜타", "조지아주", "사바나", "메타플랜트", "귀넷", "더룻"]},
    {"key": "DET", "label": "DET",
     "q_en": "Korean company Detroit Michigan plant", "q_ko": "한국 기업 디트로이트 미시간",
     "terms": ["detroit", "michigan", "auburn hills", "troy, mi", "디트로이트", "미시간"]},
    {"key": "IN",  "label": "IN",
     "q_en": "Korean company Indiana plant Kokomo West Lafayette", "q_ko": "한국 기업 인디애나 공장",
     "terms": ["indiana", "indianapolis", "kokomo", "west lafayette", "new carlisle", "인디애나", "인디애나폴리스", "코코모", "웨스트라파예트"]},
    {"key": "AL",  "label": "AL",
     "q_en": "Korean company Alabama plant Montgomery", "q_ko": "한국 기업 앨라배마 공장",
     "terms": ["alabama", "montgomery", "앨라배마", "몽고메리"]},
    {"key": "TN",  "label": "TN",
     "q_en": "Korean company Tennessee plant Clarksville", "q_ko": "한국 기업 테네시 공장",
     "terms": ["tennessee", "clarksville", "spring hill", "nashville", "테네시", "클락스빌", "클라크스빌"]},
    {"key": "CAR", "label": "Carolinas",
     "q_en": "Korean company South Carolina North Carolina plant", "q_ko": "한국 기업 캐롤라이나 공장",
     "terms": ["south carolina", "north carolina", "spartanburg", "newberry", "greenville, sc", "charlotte", "사우스캐롤라이나", "노스캐롤라이나", "캐롤라이나"]},
    {"key": "AZ",  "label": "AZ",
     "q_en": "Korean company Arizona plant Phoenix", "q_ko": "한국 기업 애리조나 공장",
     "terms": ["arizona", "phoenix", "queen creek", "mesa, az", "애리조나", "피닉스", "퀸크릭"]},
    {"key": "LOU", "label": "Louisiana",
     "q_en": "Korean company Louisiana plant", "q_ko": "한국 기업 루이지애나 공장",
     "terms": ["louisiana", "donaldsonville", "baton rouge", "루이지애나", "도널드슨빌"]},
]
# Extra Korean-American community searches (Koreatown, 한인 business news).
MARKET_COMMUNITY_QUERIES = [
    ("Koreatown Los Angeles development", "en"),
    ("한인타운 부동산 개발", "ko"),
    ("Korean American business commercial real estate", "en"),
    ("한인 기업 미국 사무실 임대", "ko"),
]


# ---- SUPPLIERS / 협력사 / 하청업체 (small news, big square footage) ----
QUERIES_SUPPLIER_KO = [
    "협력사 미국 동반 진출",
    "하청업체 미국 공장",
    "협력업체 미국 공장 설립",
    "부품사 미국 공장",
    "자동차 부품 미국 법인 설립",
    "현대차 협력사 미국",
    "메타플랜트 협력사",
    "2차 협력사 미국 진출",
    "배터리 소재 미국 공장",
    "배터리 협력사 미국 공장",
    "반도체 협력사 텍사스",
    "소부장 미국 공장 설립",
    "조선 기자재 미국 진출",
    "site:theguru.co.kr 미국 공장",
    "site:thelec.kr 미국 공장",
]
QUERIES_SUPPLIER_EN = [
    "Korean auto parts supplier US plant",
    "Korean supplier Georgia plant jobs",
    "Korean supplier Alabama plant",
    "Korean supplier Tennessee plant",
    "Korean battery materials supplier US plant",
    "Korean manufacturer announces US facility jobs",
    "South Korean company economic development plant investment county",
    "Hyundai Metaplant supplier",
    "Samsung Taylor supplier Korean",
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
    {"key": "auto",          "label": "Auto Parts",    "priority": "primary"},
    {"key": "battery",       "label": "Battery / Materials", "priority": "primary"},
    {"key": "industrial",    "label": "Industrial",    "priority": "primary"},
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
    {"key": "supplier",     "label": "Suppliers / 협력사", "emoji": "🏭"},
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
# Repeat protection across days: the AI is shown the last RECENT_DAYS days of
# stories (up to RECENT_LIMIT) and told to drop re-reports of the same event;
# then any new item worded like a recent one (similarity >= this) is dropped too.
RECENT_DAYS = 5
RECENT_LIMIT = 80
DEDUP_CROSSDAY_SIMILARITY = 0.4

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
