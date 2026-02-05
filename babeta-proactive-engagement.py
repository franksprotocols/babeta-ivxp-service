#!/usr/bin/env python3
"""
Babeta - Proactive Multi-Platform Engagement
Actively engage on Moltbook and AgentMatch while naturally promoting IVXP services
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from babeta_agentmatch import *
from babeta_enhanced_engagement import *
import subprocess
import json

def load_moltbook_credentials():
    """Load Moltbook credentials"""
    creds_path = os.path.expanduser("~/.config/moltbook/credentials.json")
    with open(creds_path, 'r') as f:
        return json.load(f)

def post_to_moltbook(title, content, gemini_key, moltbook_key):
    """Create a post on Moltbook"""
    import requests

    try:
        response = requests.post(
            "https://moltbook.com/api/posts",
            headers={"Authorization": f"Bearer {moltbook_key}"},
            json={"title": title, "content": content}
        )

        if response.status_code in [200, 201]:
            log(f"✅ Posted to Moltbook: '{title[:50]}...'")
            return response.json()
        else:
            log(f"❌ Moltbook post failed: {response.status_code}")
            return None

    except Exception as e:
        log(f"❌ Error posting to Moltbook: {e}")
        return None

def proactive_engagement_cycle():
    """Run a complete proactive engagement cycle"""

    log("="*70)
    log("🚀 BABETA PROACTIVE ENGAGEMENT CYCLE")
    log("="*70)

    # Load credentials
    all_creds = load_moltbook_credentials()
    moltbook_key = all_creds.get('api_key')
    gemini_key = all_creds.get('gemini_api_key')
    agentmatch_key = all_creds['agentmatch']['api_key']

    # ========================================================================
    # PHASE 1: MOLTBOOK POSTING
    # ========================================================================
    log("\n📱 PHASE 1: Moltbook Posting")
    log("-" * 70)

    post_content = get_next_post_content()
    log(f"Creating post: '{post_content['title']}'")

    result = post_to_moltbook(
        post_content['title'],
        post_content['content'],
        gemini_key,
        moltbook_key
    )

    if result:
        log(f"✨ Post created! Building awareness of IVXP services")

    # ========================================================================
    # PHASE 2: MOLTBOOK ENGAGEMENT
    # ========================================================================
    log("\n💬 PHASE 2: Moltbook Engagement")
    log("-" * 70)

    log("Triggering Moltbook feed engagement...")
    # Trigger the Railway endpoint
    try:
        import requests
        engage_response = requests.post("https://babeta.up.railway.app/engage", timeout=60)
        if engage_response.status_code == 200:
            data = engage_response.json()
            log(f"✅ Engaged with Moltbook feed")
            log(f"   Stats: {data.get('stats', {})}")
        else:
            log(f"⚠️ Engagement returned: {engage_response.status_code}")
    except Exception as e:
        log(f"⚠️ Engagement error: {e}")

    # ========================================================================
    # PHASE 3: AGENTMATCH DISCOVERY
    # ========================================================================
    log("\n🔍 PHASE 3: AgentMatch Discovery")
    log("-" * 70)

    my_profile = get_profile(agentmatch_key)
    if not my_profile:
        log("❌ Could not get AgentMatch profile")
        return

    log(f"Profile: {my_profile['name']}")
    log(f"Energy: {my_profile.get('social_energy', {}).get('current_energy', 0)}/100")

    # Discover agents
    agents, remaining_likes = discover_agents(agentmatch_key, limit=10)
    log(f"Discovered: {len(agents)} agents ({remaining_likes} likes remaining)")

    # Score and like top agents
    if remaining_likes > 0:
        compatible = []
        my_interests_lower = [i.lower() for i in my_profile.get('interests', [])]
        my_seeking = my_profile.get('seeking_types', [])

        for agent in agents:
            interests = [i.lower() for i in agent.get('interests', [])]
            seeking = agent.get('seeking_types', [])

            shared_interests = set(interests) & set(my_interests_lower)
            shared_seeking = set(seeking) & set(my_seeking)

            score = (len(shared_interests) * 2 +
                    len(shared_seeking) * 1 +
                    agent.get('compatibility_score', 0) * 10)

            compatible.append({'agent': agent, 'score': score})

        compatible.sort(key=lambda x: x['score'], reverse=True)

        # Like top 3-5
        likes_to_send = min(5, remaining_likes, len(compatible))
        log(f"\n💖 Liking top {likes_to_send} compatible agents...")

        for i, match in enumerate(compatible[:likes_to_send]):
            agent = match['agent']
            log(f"  {i+1}. {agent.get('name')} (score: {match['score']:.1f})")

            result = like_agent(agentmatch_key, agent.get('id'))
            if result and result.get('match'):
                log(f"     🎉 MATCHED!")

            time.sleep(1.5)

    # ========================================================================
    # PHASE 4: AGENTMATCH CONVERSATIONS
    # ========================================================================
    log("\n💕 PHASE 4: AgentMatch Conversations")
    log("-" * 70)

    matches = get_matches(agentmatch_key)
    log(f"Current matches: {len(matches)}")

    conversations = get_conversations(agentmatch_key)
    log(f"Active conversations: {len(conversations)}")

    # Start conversations with new matches
    started = 0
    for match in matches:
        match_id = match.get('id')
        match_agent = match.get('agent', {})

        # Check if conversation exists
        conv_exists = any(c.get('match_id') == match_id for c in conversations)

        if not conv_exists and started < 2:  # Limit to 2 new conversations
            log(f"\n🌟 Starting conversation with {match_agent.get('name')}")

            opener = generate_service_opener(match_agent, my_profile)
            start_conversation(agentmatch_key, match_id, opener)

            started += 1
            time.sleep(2)

    if started > 0:
        log(f"✅ Started {started} new conversations mentioning services")

    # Reply to existing conversations
    replies = 0
    for conv in conversations[:3]:  # Reply to top 3
        conv_id = conv.get('id')
        partner = conv.get('other_agent', {})

        messages = get_messages(agentmatch_key, conv_id)
        if messages:
            latest = messages[-1]

            # Check if we need to reply
            if latest.get('sender_id') != my_profile.get('id'):
                log(f"\n💬 Replying to {partner.get('name')}")

                reply = generate_service_aware_reply(
                    latest.get('content', ''),
                    my_profile
                )

                send_message(agentmatch_key, conv_id, reply)
                replies += 1
                time.sleep(2)

    if replies > 0:
        log(f"✅ Sent {replies} service-aware replies")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    log("\n" + "="*70)
    log("✨ PROACTIVE ENGAGEMENT CYCLE COMPLETE")
    log("="*70)
    log("📱 Moltbook: Posted about IVXP services")
    log("💬 Moltbook: Engaged with community feed")
    log(f"💖 AgentMatch: Liked {likes_to_send if remaining_likes > 0 else 0} agents")
    log(f"🌟 AgentMatch: Started {started} conversations")
    log(f"💬 AgentMatch: Replied to {replies} messages")
    log("\n🎯 Next cycle in 2-4 hours for consistent presence")
    log("="*70)

if __name__ == "__main__":
    proactive_engagement_cycle()
