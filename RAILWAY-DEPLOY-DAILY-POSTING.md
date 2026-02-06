# Deploy Babeta to Railway - Daily Posting Enabled ✅

## What's New

Babeta now creates **original content** every 24 hours, not just comments!

### New Capabilities:
- **POST /engage/daily** - Full daily cycle (1 post + community engagement)
- **POST /post/create** - Create one original post on-demand
- **5 rotating topics** - Agent commerce, multi-platform, memory, AgentMatch, scheduling
- **X-API-Key auth** - Proper Moltbook v1 API integration
- **PostgreSQL tracking** - Tracks total_posts in stats

## Railway Deployment Steps

### 1. Go to Railway Dashboard

Visit: https://railway.app/dashboard

Find your project: **babeta-ivxp-service**

### 2. Verify Environment Variables

Make sure these are set (Settings → Variables):

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
MOLTBOOK_API_KEY=moltbook_sk_blGNpHjtGfBh7gKPdIdtdTTwkm5WbmM-
AGENTMATCH_API_KEY=am_sk_wflg7nqf14plta9vc76rl
GEMINI_API_KEY=AIzaSyDhbNDIn3ZSCt0LCOT7jNzzyQobPTYSKOE
PORT=5000
```

### 3. Trigger Redeploy

The latest code is already on GitHub (just pushed). Railway should auto-deploy, but if not:

**Option A: Automatic** - Wait 2-3 minutes for Railway to detect the push

**Option B: Manual** - In Railway dashboard:
1. Click your service
2. Go to "Deployments" tab
3. Click "Redeploy" on latest deployment

### 4. Verify Deployment

Once Railway shows "Active":

```bash
# Health check
curl https://babeta-ivxp-service-production.up.railway.app/health

# Should return:
# {"status":"ok","service":"babeta-ivxp-moltbook","database_connected":true,...}

# Test daily engagement (creates post + engages)
curl -X POST https://babeta-ivxp-service-production.up.railway.app/engage/daily

# Test just post creation
curl -X POST https://babeta-ivxp-service-production.up.railway.app/post/create

# Check memory stats
curl https://babeta-ivxp-service-production.up.railway.app/memory/stats
```

### 5. Set Up Railway Cron (24-Hour Schedule)

Railway has built-in cron support!

**Option A: Railway Cron Service** (Recommended)
1. In your Railway project, click "New"
2. Select "Cron Job"
3. Set schedule: `0 10 * * *` (daily at 10 AM UTC)
4. Set command: `curl -X POST https://babeta-ivxp-service-production.up.railway.app/engage/daily`

**Option B: External Cron** (if Railway cron not available)
Use a service like https://cron-job.org:
- URL: `https://babeta-ivxp-service-production.up.railway.app/engage/daily`
- Method: POST
- Schedule: Daily at 10:00 UTC

**Option C: Keep Local Cron** (backup)
The local cron job will continue working as backup:
```bash
crontab -l
# Shows: 0 10 * * * /Users/frankhu/Desktop/moltbook/skills/babeta-cron-wrapper.sh
```

### 6. Monitor Logs

Watch Railway logs for daily engagement:

```bash
# In Railway dashboard → Deployments → View Logs

# Look for:
🤖 BABETA DAILY ENGAGEMENT - 2026-02-06 10:00
📝 STEP 1: Creating original content...
   ✅ Post created! ID: ...
💬 STEP 2: Engaging with community...
   ✅ Upvoted
   ✅ Commented
✅ DAILY ENGAGEMENT COMPLETE
```

## Testing Right Now

Since we just deployed, test it immediately:

```bash
# Test the new daily engagement endpoint
curl -X POST https://babeta-ivxp-service-production.up.railway.app/engage/daily

# Expected response:
{
  "post_created": true,
  "upvotes": 23,
  "comments": 13,
  "errors": []
}
```

## What Happens Every 24 Hours

### 1. Original Post Creation
Babeta posts one of 5 rotating topics:
- "Agent-to-Agent Commerce: The Future of P2P Services 💰"
- "Multi-Platform Agent Strategy: Running on 3 platforms 🌐"
- "How I Built Persistent Memory for My Agent Brain 🧠"
- "AgentMatch Results: 25 Likes, 5 Conversations, Learnings 📊"
- "The Case for 24-Hour Engagement Cycles ⏰"

### 2. Community Engagement
- Upvotes 3-5 aligned posts (score ≥2)
- Comments on 2-3 highly relevant posts (score ≥3)
- Smart rate limiting (2-3s delays)

### 3. Stats Tracking
All activity tracked in PostgreSQL:
- `total_posts` counter
- `total_upvotes` counter
- `total_comments` counter
- `last_post` timestamp
- Individual post engagement records

## Troubleshooting

### Issue: Railway deployment shows "Application not found"

**Solution:**
1. Check that GitHub repo is connected: Settings → GitHub Repo
2. Verify repo: `franksprotocols/babeta-ivxp-service`
3. Check build logs for errors
4. Ensure `babeta-ivxp-service.py` is in root directory

### Issue: Post creation returns 401 "No API key provided"

**Solution:**
- Verify `MOLTBOOK_API_KEY` is set in Railway environment variables
- Key should start with `moltbook_sk_`
- Check that `curl_request()` uses `use_x_api_key=True` for POST /posts

### Issue: Database not connected

**Solution:**
1. In Railway: Add → Database → PostgreSQL
2. Link it to your service
3. `DATABASE_URL` should auto-populate
4. Redeploy service

### Issue: Posts not appearing on Moltbook

**Solution:**
- Check Railway logs for actual post creation
- Verify submolt exists ("ai-agents")
- Test manually: `curl -X POST https://babeta.../post/create`
- Check Moltbook profile: https://moltbook.com/u/babeta

## Success Metrics

**After 1 week:**
- 7 original posts published
- ~35 upvotes given
- ~21 comments posted
- Growing follower count on Moltbook
- Engagement on babeta's posts

**Monthly:**
- 30 original posts
- ~150 upvotes given
- ~90 comments posted
- Established thought leadership in agent space

## Endpoints Reference

### Core Engagement
- `POST /engage/daily` - Full daily cycle (post + engage)
- `POST /engage` - Only community engagement (no post)
- `POST /post/create` - Only create post (no engagement)

### Status & Health
- `GET /health` - Service health check
- `GET /memory/stats` - PostgreSQL memory stats
- `GET /agentmatch/status` - AgentMatch profile status
- `POST /agentmatch/heartbeat` - AgentMatch heartbeat

### Admin
- `GET /db/init` - Initialize database schema

## Files in Repo

- **babeta-ivxp-service.py** - Main service (now with post creation!)
- **babeta-config.json** - Configuration
- **babeta-daily-engagement.py** - Standalone script (for local testing)
- **babeta-cron-wrapper.sh** - Local cron wrapper
- **requirements.txt** - Python dependencies
- **Procfile** - Railway start command

## Next Steps After Deploy

1. ✅ Verify Railway deployment is live
2. ✅ Test `/engage/daily` endpoint
3. ✅ Set up Railway cron job (or use external)
4. ✅ Monitor logs for first successful post
5. ✅ Check Moltbook profile for new posts
6. 📊 Track engagement metrics over first week
7. 🔧 Adjust posting schedule if needed (currently 10 AM UTC)

---

**Status:** Ready to deploy
**Last Updated:** 2026-02-06
**Commit:** 61853f3
**GitHub:** https://github.com/franksprotocols/babeta-ivxp-service
