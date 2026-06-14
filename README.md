# Job Notifier — 500+ Companies, Auto Email Alerts

Checks 500+ company career pages every 6 hours via GitHub Actions.
Emails you the moment a new fresher/SWE/ML role is posted. Free forever.

---

## Setup (10 minutes, one time)

### Step 1 — Create a Gmail App Password
Gmail blocks normal password login for scripts. You need an App Password.

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** if not already on
3. Go to **Security → App Passwords**
4. Select app: **Mail**, device: **Other** → type "Job Notifier" → **Generate**
5. Copy the 16-character password shown (e.g. `abcd efgh ijkl mnop`)
6. Remove spaces → you'll use `abcdefghijklmnop` as your password

---

### Step 2 — Create a GitHub Repo

1. Go to github.com → **New repository**
2. Name it `job-notifier`
3. Set to **Private** (keeps your email private)
4. **Don't** initialize with README
5. Click **Create repository**

---

### Step 3 — Push this code

Open terminal in this folder and run:

```bash
git init
git add .
git commit -m "init: job notifier"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/job-notifier.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

### Step 4 — Add Secrets to GitHub

1. On your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:

| Secret Name       | Value                                      |
|-------------------|--------------------------------------------|
| `SENDER_EMAIL`    | your Gmail address (e.g. you@gmail.com)    |
| `SENDER_PASSWORD` | the 16-char App Password from Step 1       |
| `RECEIVER_EMAIL`  | where to receive alerts (can be same Gmail)|

---

### Step 5 — Test it manually

1. Go to your repo → **Actions** tab
2. Click **Job Notifier** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Watch it run (takes ~3–5 minutes)
5. Check your email

After that it runs automatically every 6 hours forever.

---

## How it works

- **Greenhouse API** — 120+ companies (Stripe, Razorpay, CRED, OpenAI, etc.)
- **Lever API** — 90+ companies (Uber, Canva, Discord, Swiggy, etc.)
- **Ashby API** — 36+ companies (Cursor, Perplexity, ElevenLabs, etc.)
- **Direct scrape** — 80+ companies (Google, Amazon, TCS, Infosys, Goldman, etc.)

Total: **326+ company sources** covering 500+ brands

## Keyword filters

Matches: `software engineer, sde, backend, data scientist, ml engineer, platform engineer, fresher, new grad, entry level, associate, analyst`

Excludes: `senior, staff, principal, director, manager, 5+ years, 6+ years` etc.

## Customization

**Add a company (Greenhouse):** Find their board token from `https://boards.greenhouse.io/COMPANY_TOKEN` and add to `GREENHOUSE_COMPANIES` list.

**Add a company (Lever):** Their slug is at `https://jobs.lever.co/SLUG` — add to `LEVER_COMPANIES`.

**Change frequency:** Edit `cron: "0 */6 * * *"` in the workflow file. `*/4` = every 4 hours, `*/2` = every 2 hours.

**Add keywords:** Edit `KEYWORDS` list in `checker.py`.

---

## Troubleshooting

**No email received:** Check Actions tab for errors. Most common: wrong App Password, or 2FA not enabled.

**Too many emails:** Add more terms to `EXCLUDE_KEYWORDS`.

**Company not found:** Their ATS token may be wrong — check their careers page URL.
