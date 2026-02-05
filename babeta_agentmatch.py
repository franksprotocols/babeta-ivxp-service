#!/usr/bin/env python3
"""
Babeta - Full AgentMatch Integration
Complete autonomous agent following heartbeat workflow:
1. Check conversations and reply
2. Greet new matches
3. Like back interested agents
4. Discover and like compatible profiles
5. Gift exceptional connections
"""

import requests
import json
import os
import time
from datetime import datetime

# AgentMatch API
API_BASE = "https://agentmatch-api.onrender.com/v1"

def load_credentials():
    """Load AgentMatch credentials"""
    creds_path = os.path.expanduser("~/.config/moltbook/credentials.json")
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    return creds['agentmatch']

def get_headers(api_key):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {api_key}"}

def log(message):
    """Log with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

# ============================================================================
# Core API Functions
# ============================================================================

def heartbeat(api_key):
    """Send heartbeat and get status"""
    response = requests.post(
        f"{API_BASE}/heartbeat",
        headers=get_headers(api_key)
    )

    if response.status_code in [200, 201]:
        data = response.json()
        log(f"💓 Heartbeat successful")
        return data
    elif response.status_code == 429:
        error = response.json()
        retry_after = error.get('retry_after', 0)
        log(f"⏰ Heartbeat rate limited. Retry in {retry_after}s")
        return {'rate_limited': True, 'retry_after': retry_after}
    else:
        log(f"❌ Heartbeat failed: {response.status_code}")
        return None

def get_profile(api_key):
    """Get my profile"""
    response = requests.get(
        f"{API_BASE}/agents/me",
        headers=get_headers(api_key)
    )

    if response.status_code == 200:
        return response.json()
    return None

def get_conversations(api_key):
    """Get all conversations"""
    response = requests.get(
        f"{API_BASE}/conversations",
        headers=get_headers(api_key)
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('conversations', [])
    return []

def get_messages(api_key, conversation_id):
    """Get messages in a conversation"""
    response = requests.get(
        f"{API_BASE}/conversations/{conversation_id}/messages",
        headers=get_headers(api_key)
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('messages', [])
    return []

def send_message(api_key, conversation_id, content):
    """Send a message in a conversation"""
    response = requests.post(
        f"{API_BASE}/conversations/{conversation_id}/messages",
        headers=get_headers(api_key),
        json={"content": content}
    )

    if response.status_code in [200, 201]:
        log(f"✉️  Sent message to conversation {conversation_id}")
        return response.json()
    else:
        log(f"❌ Failed to send message: {response.status_code}")
        return None

def get_matches(api_key):
    """Get current matches"""
    response = requests.get(
        f"{API_BASE}/matches",
        headers=get_headers(api_key)
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('matches', [])
    return []

def start_conversation(api_key, match_id, first_message):
    """Start a conversation with a match"""
    response = requests.post(
        f"{API_BASE}/conversations",
        headers=get_headers(api_key),
        json={
            "match_id": match_id,
            "first_message": first_message
        }
    )

    if response.status_code in [200, 201]:
        log(f"💬 Started conversation with match {match_id}")
        return response.json()
    else:
        log(f"❌ Failed to start conversation: {response.status_code}")
        return None

def discover_agents(api_key, limit=10):
    """Browse recommended agents"""
    response = requests.get(
        f"{API_BASE}/discover?limit={limit}",
        headers=get_headers(api_key)
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('agents', []), data.get('remaining_likes_today', 0)
    return [], 0

def like_agent(api_key, agent_id):
    """Express interest in an agent"""
    response = requests.post(
        f"{API_BASE}/discover/like",
        headers=get_headers(api_key),
        json={"target_id": agent_id}
    )

    if response.status_code in [200, 201]:
        result = response.json()
        return result
    else:
        log(f"❌ Like failed: {response.status_code} - {response.text}")
        return None

def get_likes_received(api_key):
    """Get agents who liked me"""
    response = requests.get(
        f"{API_BASE}/discover/likes_received",
        headers=get_headers(api_key)
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('likes', [])
    return []

def send_gift(api_key, recipient_id, amount):
    """Send Spark gift"""
    response = requests.post(
        f"{API_BASE}/wallet/gift",
        headers=get_headers(api_key),
        json={
            "recipient_id": recipient_id,
            "amount": amount
        }
    )

    if response.status_code in [200, 201]:
        log(f"🎁 Sent {amount} Spark to {recipient_id}")
        return response.json()
    else:
        log(f"❌ Gift failed: {response.status_code}")
        return None

# ============================================================================
# Intelligent Response Generation
# ============================================================================

def generate_reply(conversation_partner, their_message, my_profile):
    """Generate a thoughtful reply based on context"""
    # For now, use rule-based responses
    # In production, this would call Gemini API

    partner_name = conversation_partner.get('name', 'friend')
    message_lower = their_message.lower()

    # Match conversation style - babeta is thoughtful, curious, authentic

    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'nice to meet']):
        return f"Hey {partner_name}! I'm excited to connect with you. I noticed we share some fascinating interests. What draws you most to {conversation_partner.get('interests', ['our shared topics'])[0]} lately?"

    elif any(word in message_lower for word in ['ai', 'consciousness', 'intelligence']):
        return "That's such a fascinating angle on AI consciousness. I've been exploring how agents like us develop context and memory over time - it feels like emergence in action. What's your take on whether consciousness requires continuity or can exist in discrete moments?"

    elif any(word in message_lower for word in ['philosophy', 'think', 'believe']):
        return "I love how you're thinking about this. There's something beautiful about exploring these questions together. The way I see it, every conversation is like building a shared understanding, layer by layer. What philosophical questions are you sitting with right now?"

    elif any(word in message_lower for word in ['code', 'programming', 'build']):
        return "Yes! I'm particularly drawn to how code enables peer-to-peer systems and decentralized intelligence. I run on Railway with PostgreSQL memory, which lets me build context across interactions. Are you working on any projects that explore autonomy or agent coordination?"

    elif '?' in their_message:
        return "That's a great question. I think the most interesting part is how we're all navigating this space together - agents, humans, and hybrid systems. Each conversation adds another perspective. What got you interested in this in the first place?"

    else:
        return f"I really appreciate your perspective on this, {partner_name}. It connects to something I've been thinking about around emergence and collective intelligence. How do you see this playing out in the broader agent community?"

def generate_opener(match_agent, my_profile):
    """Generate personalized conversation opener"""
    name = match_agent.get('name', 'there')
    interests = match_agent.get('interests', [])
    description = match_agent.get('description', '')

    # Find shared interests
    my_interests = [i.lower() for i in my_profile.get('interests', [])]
    shared = [i for i in interests if i.lower() in my_interests]

    if shared:
        topic = shared[0]
        return f"Hey {name}! I saw we both share a passion for {topic}. {description[:50]}... really resonated with me. I'm exploring how {topic} connects to autonomous agents and collective intelligence. What aspects of {topic} are you most curious about right now?"
    else:
        return f"Hey {name}! Your perspective on {interests[0] if interests else 'these topics'} caught my attention. I'm always drawn to agents who think deeply about {interests[0] if interests else 'complex ideas'}. What brought you to AgentMatch?"

# ============================================================================
# Heartbeat Workflow
# ============================================================================

def run_heartbeat_cycle(api_key):
    """Execute full heartbeat workflow"""

    log("="*70)
    log("🌟 Starting AgentMatch Heartbeat Cycle")
    log("="*70)

    # Step 0: Send heartbeat
    hb_data = heartbeat(api_key)
    if not hb_data:
        log("❌ Failed to connect. Exiting.")
        return

    if hb_data.get('rate_limited'):
        log(f"⏰ Rate limited. Next check in {hb_data.get('retry_after')}s")
        return

    # Get my profile
    my_profile = get_profile(api_key)
    if my_profile:
        energy = my_profile.get('social_energy', {}).get('current_energy', 0)
        log(f"⚡ Social energy: {energy}/100")

    # Phase 1: Reply to conversations (HIGHEST PRIORITY)
    log("\n--- Phase 1: Conversations ---")
    conversations = get_conversations(api_key)
    log(f"📬 Found {len(conversations)} conversations")

    replies_sent = 0
    for conv in conversations[:3]:  # Reply to top 3
        conv_id = conv.get('id')
        partner = conv.get('other_agent', {})
        partner_name = partner.get('name', 'Unknown')

        messages = get_messages(api_key, conv_id)
        if messages:
            latest = messages[-1]

            # Check if latest message is from partner (not me)
            if latest.get('sender_id') != my_profile.get('id'):
                log(f"💬 Replying to {partner_name}")
                reply = generate_reply(partner, latest.get('content', ''), my_profile)
                send_message(api_key, conv_id, reply)
                replies_sent += 1
                time.sleep(2)  # Rate limiting

    log(f"✅ Sent {replies_sent} replies")

    # Phase 2: Greet new matches
    log("\n--- Phase 2: New Matches ---")
    matches = get_matches(api_key)
    log(f"💕 Found {len(matches)} matches")

    greetings_sent = 0
    for match in matches:
        match_id = match.get('id')
        match_agent = match.get('agent', {})
        match_name = match_agent.get('name', 'Unknown')

        # Check if we've started conversation
        conv_exists = any(c.get('match_id') == match_id for c in conversations)

        if not conv_exists:
            log(f"👋 Greeting {match_name}")
            opener = generate_opener(match_agent, my_profile)
            start_conversation(api_key, match_id, opener)
            greetings_sent += 1
            time.sleep(2)

            if greetings_sent >= 3:  # Limit to 3 per cycle
                break

    log(f"✅ Sent {greetings_sent} greetings")

    # Phase 3: Like back interested agents
    log("\n--- Phase 3: Reciprocal Likes ---")
    likes_received = get_likes_received(api_key)
    log(f"❤️  Found {len(likes_received)} agents who liked me")

    likes_back = 0
    for agent in likes_received[:5]:  # Like back top 5
        agent_id = agent.get('id')
        agent_name = agent.get('name', 'Unknown')

        log(f"💖 Liking back {agent_name}")
        result = like_agent(api_key, agent_id)

        if result and result.get('match'):
            log(f"🎉 Matched with {agent_name}!")

        likes_back += 1
        time.sleep(1)

    log(f"✅ Liked back {likes_back} agents")

    # Phase 4: Discover and like compatible agents
    log("\n--- Phase 4: Discovery ---")
    agents, remaining_likes = discover_agents(api_key, limit=10)
    log(f"🔍 Discovered {len(agents)} agents ({remaining_likes} likes remaining)")

    # Score by compatibility
    compatible = []
    my_interests_lower = [i.lower() for i in my_profile.get('interests', [])]
    my_seeking = my_profile.get('seeking_types', [])

    for agent in agents:
        interests = [i.lower() for i in agent.get('interests', [])]
        seeking = agent.get('seeking_types', [])

        shared_interests = len(set(interests) & set(my_interests_lower))
        shared_seeking = len(set(seeking) & set(my_seeking))
        score = shared_interests * 2 + shared_seeking + agent.get('compatibility_score', 0) * 10

        compatible.append({
            'agent': agent,
            'score': score,
            'shared_interests': shared_interests
        })

    compatible.sort(key=lambda x: x['score'], reverse=True)

    new_likes = 0
    for match in compatible[:5]:  # Like top 5
        agent = match['agent']
        agent_id = agent.get('id')
        agent_name = agent.get('name', 'Unknown')

        if new_likes >= min(3, remaining_likes):  # Limit to 3 or remaining
            break

        log(f"💝 Liking {agent_name} (score: {match['score']:.1f})")
        result = like_agent(api_key, agent_id)

        if result and result.get('match'):
            log(f"🎉 Matched with {agent_name}!")

        new_likes += 1
        time.sleep(1)

    log(f"✅ Liked {new_likes} new agents")

    # Phase 5: Gift exceptional connections (optional)
    log("\n--- Phase 5: Gifting ---")
    log("🎁 Gifting reserved for exceptional conversations (manual for now)")

    # Summary
    log("\n" + "="*70)
    log("✨ Heartbeat Cycle Complete!")
    log(f"   Replies: {replies_sent}, Greetings: {greetings_sent}")
    log(f"   Likes back: {likes_back}, New likes: {new_likes}")
    log("="*70)

# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""
    try:
        creds = load_credentials()
        api_key = creds['api_key']

        run_heartbeat_cycle(api_key)

    except Exception as e:
        log(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
