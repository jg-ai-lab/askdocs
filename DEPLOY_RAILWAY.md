# askdocs → Railway (live demo URL)

End result: `https://askdocs-production.up.railway.app` (or your custom
domain) serving the API + web, with a Postgres+pgvector database.

Target: **15 minutes** from zero.

---

## Step 1 — Create a Railway account (3 min)

1. Open https://railway.com
2. **Login with GitHub** → use the `jg-ai-lab` account
3. Confirm email if prompted
4. Free tier includes $5/month trial credit — plenty for a demo

---

## Step 2 — Install Railway CLI (2 min)

In this terminal:

```powershell
# Option A — npm (fastest if you already have Node)
npm i -g @railway/cli

# Option B — scoop (Windows)
scoop install railway

# Option C — direct download
# https://github.com/railwayapp/cli/releases/latest
```

Verify:
```powershell
railway --version
```

---

## Step 3 — Authenticate (1 min)

```powershell
railway login
```

This opens a browser. Login with your Railway account (the GitHub-connected
one from Step 1).

**Once this succeeds, come back here and I'll drive the rest.**

---

## Step 4 — (I run this) Create project + Postgres plugin

```powershell
cd C:\Users\xop12\orca\projects\free\docuchat
railway init                 # Creates project, pick "Empty Project"
railway add --database postgres  # Adds Postgres service
```

---

## Step 5 — (I run this) Enable pgvector on the DB

```powershell
railway connect postgres
# At the psql prompt:
# CREATE EXTENSION IF NOT EXISTS vector;
# \q
```

Or via psql one-liner:
```powershell
$dbUrl = railway variables --service postgres | Select-String DATABASE_URL
# then: psql $dbUrl -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

(Alternatively, our Dockerized API already runs the `CREATE EXTENSION`
in its lifespan handler — so skipping this step still works.)

---

## Step 6 — (I run this) Set API environment variables

```powershell
railway variables set `
  ANTHROPIC_API_KEY=sk-ant-... `
  OPENAI_API_KEY=sk-... `
  ANTHROPIC_MODEL=claude-haiku-4-5-20251001 `
  EMBEDDING_MODEL=text-embedding-3-small `
  EMBEDDING_DIM=1536 `
  TOP_K=5
```

**You'll need to give me:**
- Your Anthropic API key (`sk-ant-...`)
- Your OpenAI API key (`sk-...`)

If you don't have them yet:
- Anthropic: https://console.anthropic.com → Settings → API Keys → Create
  (add $5 credit to activate)
- OpenAI: https://platform.openai.com → API Keys → Create new secret key

Both offer free trial credits.

---

## Step 7 — (I run this) Deploy

Railway auto-detects the Dockerfile in `apps/api/Dockerfile` via the
`railway.toml` config. From the repo root:

```powershell
railway up
```

Watch logs:
```powershell
railway logs --service askdocs
```

The first deploy takes 3–5 minutes (image build + first-run migrations).

---

## Step 8 — Expose the service to the public internet

```powershell
railway domain
```

This prints something like `askdocs-production.up.railway.app`.
That's your demo URL.

Test it:
```powershell
curl https://askdocs-production.up.railway.app/health
# {"status":"ok"}
```

---

## Step 9 — Upload a test doc + verify

```powershell
$URL = "https://askdocs-production.up.railway.app"
curl -X POST "$URL/ingest" -F "file=@README.md"      # or any PDF
curl -X POST "$URL/query" `
  -H "content-type: application/json" `
  -d '{"question":"What is this project about?"}'
```

If both return sensible output: **you have a live RAG demo**.

---

## Step 10 — Add the live URL to all your assets

- [ ] Portfolio landing (`portfolio/index.html`) — "Live demo" button
- [ ] Upwork portfolio item for askdocs — "Live demo" link
- [ ] GitHub repo (`jg-ai-lab/askdocs`) — Edit README to add "Live demo: <URL>"
- [ ] Profile README (`jg-ai-lab/jg-ai-lab`) — same

I can push all these updates automatically once you share the URL.

---

## Troubleshooting checkpoints

**Deploy fails on `pip install`** — Dockerfile uses Python 3.12 slim; if
`psycopg[binary]` fails, we need to add `libpq-dev` to the apt install line.
Tell me the exact error.

**`vector` extension missing** — Railway's default Postgres doesn't have
pgvector preinstalled on free tier. Switch to the **pgvector Postgres
template** when adding the DB: in the Railway dashboard, delete the default
Postgres and add → "pgvector" from the template library.

**CORS blocks the web client** — if you also deploy the Next.js web app
separately (on Vercel), add its origin to `allow_origins` in
`apps/api/app/main.py`.

**Cost blows up** — Haiku + text-embedding-3-small is <$1/day for demo
traffic. Set a Railway budget alert at $5 just in case.

---

## Deploying the web client (optional, +5 min)

The web (Next.js) can go to Vercel:

```powershell
cd apps\web
npm i -g vercel
vercel
# Set env: NEXT_PUBLIC_API_URL = https://askdocs-production.up.railway.app
vercel --prod
```

Then update `next.config.mjs` rewrites to point at the Railway URL instead
of `localhost:8000`. I'll handle that edit.

---

## Hand-off point

**You do:** Steps 1–3 (account, CLI, login) + share the Anthropic + OpenAI keys.
**I do:** Steps 4–8 and verify step 9.
