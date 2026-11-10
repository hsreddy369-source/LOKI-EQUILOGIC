# EquiLogic AI — 365-Day Automated Horse Racing Intelligence for GitHub

This repository runs your **9-Rule EquiLogic AI & Global Turf Intelligence Engine** automatically in the cloud **365 days a year for $0.00/month** using **GitHub Actions** and **GitHub Pages**.

---

## 1. Your 9 Horse Racing Rules Built Into This Engine (`src/equilogic_engine.py`)

1. **Rule 1 — Recent Form & Single-`'0'` Bounce-Back Relief**:
   - Rewards last-time-out winners (`1`: +18 pts), runners-up (`2`: +12 pts), and 3rd-place finishers (`3`: +8 pts).
   - **3-for-3 Podium Streak (`213`)**: Earns a **+16 Standout Consistency Bonus**.
   - **Multi-Zero Slump vs. Bounce-Back**: Multiple `'0'`s in the last 3 runs (`003`) receive a **-24 pt penalty**, whereas a single older `'0'` followed by a top-4 bounce-back (`014`, `203`) or class drop in Class 5/6 is forgiven (`-2 pts` instead of `-14 pts`).
2. **Rule 2 — Course & Distance (`C` / `D` / `CD`)**:
   - Proven **Course & Distance (`CD`)** winners earn **+20 pts**; standalone `C` or `D` winners earn **+10 pts** (`C+D` earns **+16 pts**).
   - Lightly-raced Class 5/6 improvers (`<= 4` runs or 2nd handicap start) are exempt from the unproven `CD` deduction.
3. **Rule 3 — Going Suitability**:
   - Matches today's official track condition (`Firm`, `Good to Firm`, `Good`, `Good to Soft`, `Soft`, `Heavy`, `Standard` AW) against proven historical surface performance (**+12 pts** when proven; **-5 pts** when unproven).
4. **Rule 4 — Days Since Last Run (DSLR) & Quick-Backup "Penalty-King" Turnarounds**:
   - **7–35 days**: Optimal fitness window (**+10 pts**); **36–60 days**: Neutral (**+2 pts**); **61–150 days**: Fitness check (**-8 pts**); **>150 days**: Long layoff (**-15 pts**).
   - **Class 5/6 Penalty-King Override**: Last-time-out winners returning within **1–10 days** under a fixed penalty to beat the handicapper's reassessment earn a **+26 to +34 pt Penalty-King Bonus** and full exemption from quick-backup deductions.
5. **Rule 5 — Weight & Official Rating (`OR`)**:
   - Evaluates net weight carried (after apprentice claims) against the field minimum (**+8 pts** for featherweight/bottom-weight advantage) and penalizes non-exempt penalty carriers.
6. **Rule 6 — Headgear & First-Time Equipment (`h1`, `b1`, `v1`, `p1`, `t1`)**:
   - Detects Hood (`h`), Blinkers (`b`), Visor (`v`), Cheekpieces (`p`), and Tongue-Tie (`t`), awarding **+14 pts** for first-time headgear (`h1`, `b1`, `v1`, `p1`, `t1`) and **+4 pts** for retained equipment.
7. **Rule 7 — Course & Distance Calibrated Draw Bias (Flat & AW)**:
   - Awards **+12 pts** to inside draws (`Stall 1–4`) and penalizes wide draws (`Stall 8+`, **-10 pts**) on sprints (`<= 7.5f`), while relaxing wide-stall penalties by **75%** on middle-distance trips (`>= 9.5f`).
8. **Rule 8 — Furlong Distance Transition (`1 mile = 8 furlongs`, `±1.0f` Tactical NLP Check)**:
   - **Same Distance (`±0.5f`)**: Awards **+10 pts** when paired with a last-start top-3 finish.
   - **Stepping Up (`+1.0f+`)**: Awards **+16 pts** when last-run comments note *"running on strongly / stayed on / finishing well"*, or flags *Unproven Stamina Risk* (**-10 pts**) if unbacked by stamina evidence.
   - **Dropping Back (`-1.0f+`)**: Awards **+19 pts** as a positive trainer tactic when last-run comments note *"weakened / faded / tired late"*, or flags *Early Pace Risk* (**-8 pts**) if unproven at shorter trips.
9. **Rule 9 — Race Class 1–6 Specialist Regime + Tactical Pace & Value Model**:
   - **Rule 9A (Unexposed Improvers)**: Class 5/6 runners with `<= 4` career runs or making their 2nd handicap start earn **+24 pts**.
   - **Rule 9B (Class-Dropper Relief)**: Runners dropping into *"calmer waters"* in Class 5/6 earn **+18 pts**.
   - **Rule 9C (Apprentice Claims & Class-Ceiling OR)**: Jockey claims of `5lb+` (**+12 pts**) or `3lb` (**+6 pts**) and Class-Ceiling OR leaders (`OR >= Field Max - 1`, **+10 pts**).
   - **Unclamped 100%-Normalized Probabilities & Value Edge**: Computes unclamped scores, normalizes field win probabilities to **100.00%**, maps tactical pace (`Front-Runner`, `Prominent`, `Midfield`, `Hold-Up`), and compares AI Win % against Market Implied % to highlight value bets.

---

## 2. Step-by-Step Guide for Complete GitHub Beginners

### Step 1: Create Your Free GitHub Account
1. Go to [https://github.com](https://github.com) and click **Sign up**.
2. Enter your email address, create a password, choose a username, and verify your email.

### Step 2: Create a New Repository
1. Once signed in, click the **`+`** icon in the top-right corner of GitHub and select **New repository**.
2. **Repository name**: Type `equilogic-365-ai`.
3. **Public vs. Private**: Select **Public** (Public repositories get **unlimited free GitHub Actions minutes** 365 days a year and free **GitHub Pages** hosting).
4. Check the box **Add a README file**, then click the green **Create repository** button at the bottom.

### Step 3: Upload These Project Files (Drag-and-Drop — No Coding Needed!)
1. Unzip `equilogic_365_github_repo.zip` on your computer or phone.
2. Inside your new `equilogic-365-ai` repository on GitHub, click **Add file** $ightarrow$ **Upload files**.
3. Drag and drop all the folders and files from the unzipped folder (`.github`, `src`, `racecards`, `data`, `docs`, `tests`, `requirements.txt`, and `README.md`) into the GitHub upload box.
4. Scroll to the bottom and click the green **Commit changes** button.

### Step 4: Turn On Your 365-Day AI & Run It Right Now
1. Click the **Actions** tab at the top of your GitHub repository.
2. If asked to enable workflows, click the green button **I understand my workflows, go ahead and enable them**.
3. On the left side, click **EquiLogic AI — 365-Day Horse Racing Analyst**.
4. Click the **Run workflow** dropdown button on the right, then click the green **Run workflow** button.
5. Within 30–45 seconds, you will see a green checkmark ✅! Your AI has just analyzed all racecards and updated `docs/DAILY_REPORT.md` and `docs/index.html`.

### Step 5: Turn On Your Free Live Web Dashboard (GitHub Pages)
1. Click **Settings** (top tab of your repository) $ightarrow$ click **Pages** in the left sidebar.
2. Under **Build and deployment $ightarrow$ Branch**, change `None` to **`main`**, change the folder next to it from `/ (root)` to **`/docs`**, and click **Save**.
3. Wait 1 minute and refresh the page—GitHub will give you your own permanent live website link (`https://<your-username>.github.io/equilogic-365-ai/`) showing your daily #1 AI Predicted Winners and 9-Rule flags!

### Step 6: Optional API Keys & Phone Notifications (GitHub Secrets)
If you want the AI to pull live UK/Ireland/HK racecards from [The Racing API Free Tier](https://api.theracingapi.com/documentation) (`50 requests/day` free) or send daily picks to your phone on **Telegram** or **Discord**:
1. Go to your repository **Settings** $ightarrow$ **Secrets and variables** $ightarrow$ **Actions**.
2. Click **New repository secret** and add any of these optional keys:
   - `RACING_API_USER` and `RACING_API_PASS` (from your free account at The Racing API)
   - `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (to receive daily picks on Telegram)
   - `DISCORD_WEBHOOK_URL` (to receive daily picks in a Discord channel)
