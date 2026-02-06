# Set Up Railway Cron for Daily Posting

## Option 1: Railway Cron Job (Recommended)

Railway has built-in cron support!

### Steps:

1. **In your Railway project dashboard:**
   - Click "New" button
   - Select "Cron Job"

2. **Configure the cron job:**
   - **Name:** `babeta-daily-posting`
   - **Schedule:** `0 10 * * *` (runs daily at 10:00 AM UTC)
   - **Command:**
     ```bash
     curl -X POST https://YOUR-RAILWAY-URL/engage/daily
     ```
   - Replace `YOUR-RAILWAY-URL` with your actual Railway domain

3. **Set environment variables (if needed):**
   - Usually inherits from your service
   - May need to add if it's a separate cron service

4. **Deploy and activate**

---

## Option 2: External Cron Service (Easier Setup)

Use a free external cron service like **cron-job.org**

### Steps:

1. **Go to:** https://cron-job.org (or https://easycron.com)

2. **Create free account**

3. **Add new cron job:**
   - **URL:** `https://YOUR-RAILWAY-URL/engage/daily`
   - **Method:** POST
   - **Schedule:** Daily at 10:00 AM (choose your timezone)
   - **Timeout:** 60 seconds

4. **Save and activate**

---

## Option 3: GitHub Actions (Free, Reliable)

Use GitHub Actions to trigger Railway endpoint daily.

### Steps:

1. **In your GitHub repo** (franksprotocols/babeta-ivxp-service)

2. **Create `.github/workflows/daily-engagement.yml`:**

```yaml
name: Babeta Daily Engagement

on:
  schedule:
    # Runs at 10:00 AM UTC every day
    - cron: '0 10 * * *'
  workflow_dispatch: # Allows manual trigger

jobs:
  engage:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Daily Engagement
        run: |
          curl -X POST https://YOUR-RAILWAY-URL/engage/daily
          echo "Daily engagement triggered at $(date)"
```

3. **Commit and push:**
```bash
mkdir -p .github/workflows
# Create the file above
git add .github/workflows/daily-engagement.yml
git commit -m "Add GitHub Actions daily engagement cron"
git push origin main
```

4. **Verify in GitHub:**
   - Go to repo → Actions tab
   - Should see "Babeta Daily Engagement" workflow
   - Can manually trigger with "Run workflow" button

---

## Testing the Endpoint First

Before setting up cron, test manually:

```bash
# Replace with your actual Railway URL
curl -X POST https://YOUR-RAILWAY-URL/engage/daily

# Should return:
{
  "post_created": true,
  "upvotes": 23,
  "comments": 13,
  "errors": []
}
```

---

## Which Option Should You Choose?

| Option | Pros | Cons |
|--------|------|------|
| **Railway Cron** | Native integration, same platform | May cost extra, depends on plan |
| **Cron-job.org** | Free, easy setup, visual dashboard | External dependency |
| **GitHub Actions** | Free, built into repo, reliable | Requires workflow file |

**My Recommendation:** GitHub Actions (Option 3)
- It's free
- Very reliable (GitHub's infrastructure)
- Easy to see history in Actions tab
- Can manually trigger for testing
- No external accounts needed

---

## What Happens When Cron Runs

Every 24 hours at 10:00 AM:

1. **POST request** to `/engage/daily`
2. **Railway service:**
   - Creates 1 original post (rotates through 5 topics)
   - Upvotes 3-5 community posts
   - Comments on 2-3 relevant posts
   - Updates PostgreSQL stats
3. **Returns results** with post_created, upvotes, comments count
4. **Logs everything** in Railway deployment logs

---

## Monitoring

**Check Railway logs:**
- Railway Dashboard → Deployments → View Logs
- Look for: "🤖 BABETA DAILY ENGAGEMENT"

**Check Moltbook:**
- Visit: https://moltbook.com/u/babeta
- Should see new posts daily

**Check stats:**
```bash
curl https://YOUR-RAILWAY-URL/memory/stats
```

---

## Your Railway URL

**Please provide your Railway URL from the dashboard so I can:**
1. Create the exact cron command
2. Test the endpoint
3. Set up the cron job for you

**Find it in:** Railway Dashboard → Your Service → Settings → Domains
