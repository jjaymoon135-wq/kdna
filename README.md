# Korea CRE Radar

A daily webpage that scans Korean-company news — US expansion, funding, IPOs,
supplier moves — filters it with Claude, and shows a skimmable bilingual list.
Runs itself every weekday morning. You bookmark one URL and skim it at your desk.

---

## What you get

- A page grouped by category (🇺🇸 US Expansion · 💰 Funding · 📈 IPO · 🔗 Supplier)
- Each item: one-line English summary, one-line Korean summary, source, link
- Auto-refreshes every weekday morning before you're at your desk
- Hosting + automation are **free**; the AI step costs ~**$0.50/month**

---

## One-time setup (about 15 minutes, copy-paste level)

You need: your GitHub account, and an Anthropic API key with ~$5 of credit.

### 1. Get an Anthropic API key
1. Go to **console.anthropic.com** → sign in → **Billing** → add $5 credit.
2. Go to **API Keys** → **Create Key** → copy it (starts with `sk-ant-`).
   Keep it somewhere safe for step 3.

### 2. Create the repository
1. On GitHub, click **New repository**.
2. Name it `korea-cre-radar`. Set it to **Public** (required for free Pages).
   Click **Create**.
3. On the new repo page, click **uploading an existing file**, then drag in
   ALL the files from this project, keeping the folder structure:
   ```
   generate.py
   config.py
   requirements.txt
   README.md
   .github/workflows/daily.yml
   docs/index.html
   ```
   Click **Commit changes**.

### 3. Add your API key as a secret
1. In the repo: **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret**.
3. Name: `ANTHROPIC_API_KEY` (exactly). Value: paste your `sk-ant-...` key.
   Click **Add secret**.

### 4. Turn on the webpage (GitHub Pages)
1. **Settings** → **Pages**.
2. Under **Source**, choose **Deploy from a branch**.
3. Branch: `main`, folder: `/docs`. Click **Save**.
4. After a minute, this section shows your live URL:
   `https://<your-username>.github.io/korea-cre-radar/`
   **Bookmark that.** That's your radar.

### 5. Run it once by hand to confirm it works
1. **Actions** tab → if prompted, click the green button to enable workflows.
2. Click **Korea CRE Radar** on the left → **Run workflow** → **Run workflow**.
3. Wait ~1 minute. When it finishes green, refresh your bookmarked URL.

Done. From now on it runs automatically every weekday.

---

## Everyday use

Just open your bookmark each morning. Skim titles, click what's worth reading.
Nothing to maintain.

## Changing what it catches

Open **`config.py`** on GitHub (click the file → pencil icon → edit → commit).
- Add/remove search phrases in `QUERIES_KO` and `QUERIES_EN`.
- Add anchor accounts your team tracks in `ANCHOR_COMPANIES`.
The next morning's run uses your changes.

## Changing the delivery time

Open **`.github/workflows/daily.yml`**, edit the `cron` line.
`"0 13 * * 1-5"` = 13:00 UTC (6am Pacific in summer), Mon–Fri.

---

## First two weeks: expect to tune

Out of the box it will catch too much and miss some things — that's normal.
Skim what gets through, then adjust `config.py`: tighten queries that bring
noise, add phrases for signals you missed. After ~2 weeks it settles down.

## Cost

- GitHub Pages + Actions: free.
- Anthropic API: pennies per run, well under $1/month. $5 lasts months.

## If something breaks

- **Page didn't update?** Actions tab → open the latest run → read the red step.
- **"No qualifying signals"?** Real some slow days, or your queries are too
  narrow — widen them in `config.py`.
- **Blocked domain / network error in logs?** Google News occasionally rate-
  limits; the next scheduled run usually clears it.
