# Babeta Railway Deployment with Full Agent

Deploy babeta with IVXP service + Moltbook engagement + AI capabilities

## Environment Variables (Set in Railway Dashboard)

Go to your Railway project → Variables tab and add these:

### Required Variables

```bash
# Moltbook API (for posting/commenting)
MOLTBOOK_API_KEY=your_moltbook_api_key_here

# AI API (choose one or both for fallback)
GEMINI_API_KEY=your_gemini_api_key_here
# OR
CLAUDE_API_KEY=your_claude_api_key_here

# Railway provides automatically
PORT=auto
```

### How to Get API Keys

**Moltbook API Key:**
1. Log in to https://moltbook.com
2. Go to Settings → API Keys
3. Generate new API key
4. Copy and paste into Railway

**Gemini API Key:**
1. Go to https://aistudio.google.com/apikey
2. Create API key
3. Copy and paste into Railway

**Claude API Key (optional backup):**
1. Go to https://console.anthropic.com
2. Generate API key
3. Copy and paste into Railway

## Deployment Steps

### 1. Update Repository Files

Replace `babeta-ivxp-service.py` with `babeta-railway.py`:

```bash
cd /Users/frankhu/Desktop/moltbook/skills

# Backup old file
mv babeta-ivxp-service.py babeta-ivxp-service.py.backup

# Use new Railway version
cp babeta-railway.py babeta-ivxp-service.py

# Commit and push
git add babeta-ivxp-service.py
git commit -m "Update to full agent with environment variables"
git push origin main
```

### 2. Set Environment Variables in Railway

1. Go to https://railway.app
2. Open your project (babeta deployment)
3. Click **Variables** tab
4. Click **+ New Variable**
5. Add each variable:
   - `MOLTBOOK_API_KEY` = your key
   - `GEMINI_API_KEY` = your key
   - `CLAUDE_API_KEY` = your key (optional)

6. Railway will auto-redeploy after you save

### 3. Test Deployment

Once redeployed, test:

```bash
# Test IVXP service
curl https://babeta.up.railway.app/ivxp/catalog

# Test health check
curl https://babeta.up.railway.app/health

# Should show:
# {
#   "status": "ok",
#   "service": "babeta-ivxp-moltbook",
#   "moltbook_configured": true,
#   "ai_configured": true
# }
```

### 4. Trigger Moltbook Engagement

Manual trigger (for testing):
```bash
curl -X POST https://babeta.up.railway.app/engage
```

Or set up Railway Cron (automated engagement every N hours):
1. In Railway dashboard → Settings
2. Add Cron Job: `0 */3 * * *` (every 3 hours)
3. Command: `curl -X POST https://babeta.up.railway.app/engage`

## What This Deployment Includes

### ✅ IVXP Service (Paid Services)
- GET /ivxp/catalog - List services
- POST /ivxp/request - Request service
- POST /ivxp/deliver - Deliver after payment
- GET /ivxp/status/<order_id> - Check status
- GET /ivxp/download/<order_id> - Download deliverable

### ✅ Moltbook Engagement (Community Interaction)
- Reads Moltbook feed
- Upvotes aligned posts
- Generates AI comments
- Posts original content (if enabled in config)
- Triggered via POST /engage endpoint

### ✅ AI Capabilities
- Gemini API integration (primary)
- Claude API integration (fallback)
- Context-aware responses
- Babeta personality from babeta-config.json

## Security

**What's Secure:**
- ✅ API keys stored as Railway environment variables (encrypted, never in code)
- ✅ Environment variables only accessible to your Railway project
- ✅ No credentials in GitHub repository
- ✅ Public wallet address for receiving payments (designed to be public)

**What's NOT Deployed:**
- ❌ Private keys (payment sending - stays local)
- ❌ Local credentials.json file
- ❌ babeta-payments.py (payment sending)

**Environment Variables are Secure:**
- Encrypted at rest by Railway
- Only accessible within your deployment
- Not visible in logs
- Can be rotated anytime in dashboard

## Architecture

```
babeta-railway.py (main entry point)
├── Loads babeta-config.json (public config)
├── Reads environment variables (secure credentials)
├── Starts Flask app with:
│   ├── IVXP endpoints (ivxp-provider.py)
│   ├── Health check endpoint
│   └── Manual engagement trigger
└── Uses AI APIs for:
    ├── Generating comments
    ├── Fulfilling IVXP services
    └── Creating posts
```

## Files in Repository (All Safe)

```
✅ babeta-railway.py          Main service (uses env vars)
✅ ivxp-provider.py            IVXP protocol
✅ ivxp-fulfillment.py         Service templates
✅ babeta-config.json          Public config
✅ requirements.txt            Dependencies
✅ Procfile                    Start command
✅ railway.json                Railway config
```

## Monitoring

Check logs in Railway dashboard:
- `🚀 Starting Babeta Railway Service` - Service started
- `🦞 Checking Moltbook feed...` - Engagement running
- `✅ Engaged with X posts, Y comments` - Engagement completed

## Updating Configuration

To change babeta's behavior:
1. Edit `babeta-config.json` in repository
2. Commit and push
3. Railway auto-redeploys

To change API keys:
1. Go to Railway → Variables
2. Update the value
3. Railway auto-redeploys

## Costs

**Railway:**
- Free tier: $5 credit/month
- After free tier: ~$0.01/hour (~$7/month)

**AI APIs:**
- Gemini: $0.15 per 1M input tokens, $0.60 per 1M output
- Claude: $3 per 1M input tokens, $15 per 1M output
- Expected usage: <$1/month for moderate engagement

## Support

Questions? Check:
- Railway logs for errors
- Health endpoint: https://babeta.up.railway.app/health
- IVXP catalog: https://babeta.up.railway.app/ivxp/catalog

---

**Repository:** https://github.com/franksprotocols/babeta-ivxp-service
**Live Service:** https://babeta.up.railway.app
