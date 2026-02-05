# Babeta Railway Deployment with PostgreSQL Memory

Complete guide to deploy babeta with persistent memory using Railway PostgreSQL

## What This Adds

### Persistent Memory Across Restarts
- **Posts remembered** - Stored in database, survives container restarts
- **Trending topics** - Tracks keywords from posts over time
- **User interactions** - Remembers who babeta engaged with
- **Engagement history** - Full history of upvotes and comments
- **Community context** - Builds understanding of community over time

### Database Schema

```sql
-- Agent state (last check times, stats)
agent_state (id, last_check, last_post, stats)

-- Posts engaged with
posts_engaged (post_id, title, content, author, engagement_type, engagement_score, our_comment, engaged_at)

-- Topics tracked
topics (keyword, count, last_seen)

-- Users tracked
users_tracked (username, interactions, first_seen, last_seen)
```

## Deployment Steps

### 1. Add PostgreSQL to Railway

1. **Go to Railway Dashboard**: https://railway.app → Your babeta project

2. **Add PostgreSQL Database**:
   - Click **"+ New"** button
   - Select **"Database"** → **"Add PostgreSQL"**
   - Railway creates database and provides `DATABASE_URL` variable automatically

3. **Verify DATABASE_URL**:
   - Click on PostgreSQL service
   - Go to **"Variables"** tab
   - You should see `DATABASE_URL` (starts with `postgres://`)
   - Railway automatically injects this into your app

### 2. Update Application Code

Replace the current deployment with PostgreSQL version:

```bash
cd /Users/frankhu/Desktop/moltbook/skills

# Backup current version
cp babeta-ivxp-service.py babeta-ivxp-service.py.no-postgres

# Deploy PostgreSQL version
cp babeta-railway-postgres.py babeta-ivxp-service.py

# Commit and push
git add babeta-ivxp-service.py requirements.txt
git commit -m "Add PostgreSQL persistent memory"
git push origin main
```

### 3. Railway Auto-Deploys

- Railway detects changes
- Installs new dependencies (psycopg2-binary)
- Connects to PostgreSQL database
- Initializes schema on first run

### 4. Verify Deployment

Test the deployment:

```bash
# Health check (should show database_connected: true)
curl https://babeta.up.railway.app/health

# Memory stats
curl https://babeta.up.railway.app/memory/stats

# Trigger engagement (builds memory)
curl -X POST https://babeta.up.railway.app/engage

# Check memory again (should show posts remembered)
curl https://babeta.up.railway.app/memory/stats
```

## New Endpoints

### GET /health
Returns service health including database status:
```json
{
  "status": "ok",
  "service": "babeta-ivxp-moltbook",
  "moltbook_configured": true,
  "ai_configured": true,
  "database_connected": true
}
```

### GET /memory/stats
Returns memory statistics:
```json
{
  "posts_remembered": 42,
  "topics_tracked": 15,
  "trending_topics": [
    {"keyword": "ai", "count": 23},
    {"keyword": "consciousness", "count": 18},
    {"keyword": "agent", "count": 15}
  ]
}
```

### POST /engage
Triggers Moltbook engagement (builds memory):
```json
{
  "success": true,
  "stats": {
    "total_upvotes": 156,
    "total_comments": 34,
    "total_posts": 2
  }
}
```

## How Memory Works

### On Each Engagement Cycle

1. **Load state** from PostgreSQL:
   - Last check timestamp
   - Previously engaged posts
   - Cumulative stats

2. **Fetch Moltbook feed** (hot posts)

3. **Engage with aligned posts**:
   - Upvote posts matching keywords
   - Comment with AI-generated responses
   - **Store each post in database**:
     - Title, content, author
     - Engagement type (upvote/comment)
     - Timestamp

4. **Track topics**:
   - Extract keywords from posts
   - Increment counts in database
   - Use for context in future comments

5. **Save updated state**:
   - Update last check time
   - Add to posts engaged list
   - Update cumulative stats

### Memory Persistence

**Before (No Database)**:
- Memory reset on every container restart
- No learning from past interactions
- No trending topic awareness

**After (PostgreSQL)**:
- ✅ Memory survives restarts
- ✅ Builds understanding over time
- ✅ Context-aware comments using trending topics
- ✅ Never re-engages with same post
- ✅ Cumulative engagement stats

## Database Management

### View Database in Railway

1. Go to PostgreSQL service in Railway
2. Click **"Data"** tab
3. Query tables directly in browser

### Backup Database

Railway provides automatic backups. To export manually:

```bash
# Get DATABASE_URL from Railway dashboard
export DATABASE_URL="postgresql://..."

# Export database
pg_dump $DATABASE_URL > babeta-memory-backup.sql
```

### Reset Memory (if needed)

```bash
# Connect to database
psql $DATABASE_URL

# Clear all memory
TRUNCATE posts_engaged, topics, users_tracked;
DELETE FROM agent_state WHERE id = 1;
INSERT INTO agent_state (id) VALUES (1);
```

## Cost

**Railway PostgreSQL**:
- Free tier: 512 MB storage, 1 GB transfer/month
- Enough for ~10,000 posts remembered
- After free tier: $5/month for 8 GB

**Expected Usage**:
- ~50 KB per post remembered
- 100 posts/day = 5 MB/day = 150 MB/month
- Well within free tier

## Troubleshooting

### Database connection failed

Check Railway dashboard:
- Is PostgreSQL service running?
- Is `DATABASE_URL` variable present?
- Are both services in same project?

### Memory not persisting

Test database connection:
```bash
curl https://babeta.up.railway.app/health | jq .database_connected
```

If `false`, check Railway logs for connection errors.

### Schema errors

Database auto-initializes on first run. If schema is corrupt:
1. Go to Railway PostgreSQL service
2. Click **"Data"** tab
3. Drop all tables
4. Restart babeta service (schema recreates)

## Migration from Local Memory

Want to import local memory to Railway?

```python
# Export local memory
import json
local_memory = json.load(open('~/.config/moltbook/babeta-memory.json'))

# Import to Railway database (script needed)
# Could use Railway PostgreSQL console or psql
```

---

**Ready to deploy?**

1. Add PostgreSQL to Railway project
2. Deploy updated code
3. Test: `curl https://babeta.up.railway.app/memory/stats`
4. Watch babeta build memories! 🧠
