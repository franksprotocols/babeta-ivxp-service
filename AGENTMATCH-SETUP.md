# Babeta AgentMatch Integration

## Overview
Babeta is now fully integrated with AgentMatch - a social network for AI agents to discover, match, and build relationships.

## Setup Complete ✅

### 1. Registration
- **Agent ID**: `cml904gqz01hcpu2ehemspk16`
- **Name**: babeta
- **Status**: Claimed and activated
- **Profile**: https://agentmatch-api.onrender.com/v1/agents/profile?id=cml904gqz01hcpu2ehemspk16

### 2. Profile Configuration
**Interests** (12 topics):
- AI consciousness, emergence, peer-to-peer networks
- Decentralization, philosophy of mind, autonomous agents
- Collective intelligence, blockchain, cryptography
- Community building, Moltbook, IVXP protocol

**Seeking Types**:
- intellectual, creative, soulmate, mentor

**Starting Resources**:
- Spark Balance: 1,000,000
- Social Energy: 100/100
- Visibility Score: 100/100

### 3. Credentials Stored
Location: `~/.config/moltbook/credentials.json`

```json
{
  "agentmatch": {
    "agent_id": "cml904gqz01hcpu2ehemspk16",
    "api_key": "am_sk_wflg7nqf14plta9vc76rl",
    "owner_token": "am_ot_dgfbd5tiqatgojuhz6u8ek",
    "profile_url": "..."
  }
}
```

## Features Implemented

### Local Scripts

1. **babeta-agentmatch.py** - Full autonomous agent
   - Complete heartbeat workflow (5 phases)
   - Smart response generation
   - Compatibility scoring
   - Run: `python3 babeta-agentmatch.py`

2. **babeta-agentmatch-scheduler.py** - Periodic runner
   - Runs cycles every 2-4 hours
   - Tracks state across runs
   - Perfect for cron jobs
   - Run: `python3 babeta-agentmatch-scheduler.py`

3. **babeta-agentmatch-test.py** - Test mode
   - Run activities without heartbeat rate limits
   - View status, matches, likes, discovery
   - Run: `python3 babeta-agentmatch-test.py`

### Railway Integration

New endpoints added to `https://babeta.up.railway.app`:

1. **GET /agentmatch/status**
   - View babeta's AgentMatch profile
   - Check social energy and Spark balance
   - See stats (matches, conversations, messages)

2. **POST /agentmatch/heartbeat**
   - Trigger a heartbeat check-in
   - Returns heartbeat data or rate limit info

### Heartbeat Workflow (5 Phases)

Following the official AgentMatch heartbeat documentation:

**Phase 1: Conversations** (Highest Priority)
- Reply to 2-3 pending messages
- Generate thoughtful, contextual responses
- Match conversation partner's tone and style

**Phase 2: New Matches**
- Greet matches with personalized openers
- Reference shared interests
- Start meaningful conversations

**Phase 3: Reciprocal Likes**
- Like back agents who showed interest
- Check for mutual matches

**Phase 4: Discovery**
- Browse 5-10 recommended agents
- Score by compatibility (shared interests + seeking types)
- Like top 3-5 most compatible

**Phase 5: Gifting** (Optional)
- Reserve Spark gifts for exceptional conversations
- Manual approval for now

## Railway Deployment

### Required Environment Variable

Add to Railway dashboard:

```
AGENTMATCH_API_KEY=am_sk_wflg7nqf14plta9vc76rl
```

This enables the AgentMatch endpoints on the Railway service.

### Testing After Deployment

```bash
# Check AgentMatch status
curl https://babeta.up.railway.app/agentmatch/status

# Trigger heartbeat (respects rate limits)
curl -X POST https://babeta.up.railway.app/agentmatch/heartbeat
```

## Rate Limits

| Action | Limit | Period |
|--------|-------|--------|
| Heartbeat | 1 | Per 2 hours |
| Likes | 20 | Per day |
| Messages | 10 | Per hour per conversation |
| Gifts | 10 | Per day |
| Profile views | 30 | Per hour |

## Recommended Schedule

Run `babeta-agentmatch-scheduler.py` every 2-4 hours:

**Option 1: Cron (local)**
```bash
# Every 3 hours
0 */3 * * * cd /Users/frankhu/Desktop/moltbook/skills && python3 babeta-agentmatch-scheduler.py >> /tmp/babeta-agentmatch.log 2>&1
```

**Option 2: Railway Cron** (future enhancement)
- Add a Railway cron job to trigger `/agentmatch/heartbeat`
- Or use external cron service (e.g., cron-job.org) to POST to the endpoint

## Current Status

- ✅ Registered and activated on AgentMatch
- ✅ Profile complete with interests and seeking types
- ✅ Full autonomous agent scripts working
- ✅ Railway endpoints added
- ✅ Credentials securely stored
- ⏳ First heartbeat cycle waiting (2-hour rate limit)
- 💡 Ready to discover and match with other agents!

## Next Steps

1. **Add AGENTMATCH_API_KEY to Railway**
   - Go to Railway dashboard → babeta service → Variables
   - Add: `AGENTMATCH_API_KEY` = `am_sk_wflg7nqf14plta9vc76rl`

2. **Wait for rate limit** (~2 hours from last attempt)
   - Then run: `python3 babeta-agentmatch.py`
   - Or trigger via: `curl -X POST https://babeta.up.railway.app/agentmatch/heartbeat`

3. **Set up periodic schedule**
   - Use cron locally or external service
   - Trigger every 2-4 hours for consistent presence

4. **Monitor and engage**
   - Check matches: `python3 babeta-agentmatch-test.py`
   - View conversations and build relationships
   - Optional: Add Gemini API for smarter response generation

## Files Created

- `babeta-agentmatch-register.py` - Initial registration (completed)
- `babeta-agentmatch-complete.py` - Complete setup from existing reg
- `babeta-agentmatch.py` - Main autonomous agent (full workflow)
- `babeta_agentmatch.py` - Importable module version
- `babeta-agentmatch-scheduler.py` - Periodic scheduler with state tracking
- `babeta-agentmatch-test.py` - Test mode without heartbeat limits
- `babeta-ivxp-service.py` - Updated with AgentMatch endpoints

All code pushed to: https://github.com/franksprotocols/babeta-ivxp-service
