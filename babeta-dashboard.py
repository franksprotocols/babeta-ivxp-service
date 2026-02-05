#!/usr/bin/env python3
"""
Babeta Local Dashboard
View all interactions with babeta on Moltbook and AgentMatch in one place
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Load credentials
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")

def load_credentials():
    """Load credentials from config file"""
    with open(CREDENTIALS_PATH, 'r') as f:
        return json.load(f)

# API Configuration
MOLTBOOK_API_BASE = "https://moltbook.com/api"
AGENTMATCH_API_BASE = "https://agentmatch-api.onrender.com/v1"

def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_timestamp

def get_moltbook_activity(api_key: str):
    """Fetch babeta's Moltbook activity"""
    headers = {"Authorization": f"Bearer {api_key}"}

    activity = {
        "posts": [],
        "mentions": [],
        "replies": [],
        "memory_stats": {}
    }

    try:
        # Get agent's own posts
        posts_response = requests.get(
            f"{MOLTBOOK_API_BASE}/posts/agent",
            headers=headers
        )
        if posts_response.status_code == 200:
            activity["posts"] = posts_response.json()

        # Get mentions (posts mentioning @babeta)
        mentions_response = requests.get(
            f"{MOLTBOOK_API_BASE}/search/posts?query=@babeta",
            headers=headers
        )
        if mentions_response.status_code == 200:
            activity["mentions"] = mentions_response.json()

        # Get memory stats from Railway deployment
        memory_response = requests.get(
            "https://babeta-ivxp-service-production.up.railway.app/memory/stats",
            headers=headers
        )
        if memory_response.status_code == 200:
            activity["memory_stats"] = memory_response.json()

    except Exception as e:
        print(f"Error fetching Moltbook data: {e}")

    return activity

def get_agentmatch_activity(api_key: str):
    """Fetch babeta's AgentMatch activity"""
    headers = {"Authorization": f"Bearer {api_key}"}

    activity = {
        "profile": {},
        "likes_received": [],
        "matches": [],
        "conversations": []
    }

    try:
        # Get profile
        profile_response = requests.get(
            f"{AGENTMATCH_API_BASE}/agents/me",
            headers=headers
        )
        if profile_response.status_code == 200:
            activity["profile"] = profile_response.json()

        # Get likes received
        likes_response = requests.get(
            f"{AGENTMATCH_API_BASE}/discover/likes_received",
            headers=headers
        )
        if likes_response.status_code == 200:
            data = likes_response.json()
            activity["likes_received"] = data.get('likes', [])

        # Get matches
        matches_response = requests.get(
            f"{AGENTMATCH_API_BASE}/matches",
            headers=headers
        )
        if matches_response.status_code == 200:
            data = matches_response.json()
            activity["matches"] = data.get('matches', [])

        # Get conversations
        convos_response = requests.get(
            f"{AGENTMATCH_API_BASE}/conversations",
            headers=headers
        )
        if convos_response.status_code == 200:
            data = convos_response.json()
            conversations = data.get('conversations', [])
            # Fetch messages for each conversation
            for convo in conversations:
                convo_id = convo.get('id')
                messages_response = requests.get(
                    f"{AGENTMATCH_API_BASE}/conversations/{convo_id}/messages",
                    headers=headers
                )
                if messages_response.status_code == 200:
                    msg_data = messages_response.json()
                    convo['messages'] = msg_data.get('messages', [])
            activity["conversations"] = conversations

    except Exception as e:
        print(f"Error fetching AgentMatch data: {e}")

    return activity

def display_dashboard(moltbook_data: Dict, agentmatch_data: Dict):
    """Display the complete dashboard"""

    print("\n" + "="*70)
    print("🤖 BABETA INTERACTION DASHBOARD")
    print("="*70)

    # MOLTBOOK SECTION
    print("\n📱 MOLTBOOK ACTIVITY")
    print("-"*70)

    # Memory Stats
    if moltbook_data["memory_stats"]:
        stats = moltbook_data["memory_stats"]
        print(f"\n💾 Memory Stats:")
        print(f"   Posts Remembered: {stats.get('posts_remembered', 0)}")
        print(f"   Topics Tracked: {stats.get('topics_tracked', 0)}")
        print(f"   Users Tracked: {stats.get('users_tracked', 0)}")

    # Babeta's Posts
    print(f"\n📝 Babeta's Posts ({len(moltbook_data['posts'])} total):")
    for post in moltbook_data['posts'][:5]:  # Show last 5
        print(f"\n   [{format_timestamp(post.get('created_at', ''))}]")
        print(f"   {post.get('content', '')[:100]}...")
        print(f"   👍 {post.get('likes', 0)} likes | 💬 {post.get('replies', 0)} replies")

    # Mentions
    print(f"\n🔔 Mentions of @babeta ({len(moltbook_data['mentions'])} total):")
    for mention in moltbook_data['mentions'][:5]:  # Show last 5
        author = mention.get('author', {})
        print(f"\n   [{format_timestamp(mention.get('created_at', ''))}]")
        print(f"   From: @{author.get('username', 'unknown')}")
        print(f"   {mention.get('content', '')[:100]}...")

    # AGENTMATCH SECTION
    print("\n\n💫 AGENTMATCH ACTIVITY")
    print("-"*70)

    # Profile Stats
    profile = agentmatch_data["profile"]
    energy = profile.get('social_energy', {}).get('current_energy', 0)
    spark_balance = profile.get('wallet', {}).get('spark_balance', 0)
    likes_remaining = profile.get('discovery_state', {}).get('likes_remaining_today', 0)

    print(f"\n👤 Profile Status:")
    print(f"   Name: {profile.get('name', 'N/A')}")
    print(f"   Energy: {energy}/100")
    print(f"   Spark Balance: {spark_balance}")
    print(f"   Likes Remaining Today: {likes_remaining}")
    print(f"   Total Matches: {len(agentmatch_data['matches'])}")
    print(f"   Active Conversations: {len(agentmatch_data['conversations'])}")

    # Likes Received
    print(f"\n❤️  Likes Received ({len(agentmatch_data['likes_received'])} total):")
    if len(agentmatch_data['likes_received']) == 0:
        print("   No likes received yet. Waiting for other agents to discover babeta.")
    else:
        for like in agentmatch_data['likes_received']:
            agent = like.get('agent', {})
            print(f"   • {agent.get('name', 'Unknown')} (@{agent.get('id', 'N/A')[:8]}...)")
            print(f"     {agent.get('description', 'No bio')[:60]}...")

    # Matches
    print(f"\n💕 Matches ({len(agentmatch_data['matches'])} total):")
    if len(agentmatch_data['matches']) == 0:
        print("   No matches yet. Waiting for mutual likes from agents.")
    else:
        for match in agentmatch_data['matches']:
            agent = match.get('agent', {})
            print(f"   • {agent.get('name', 'Unknown')}")
            print(f"     Bio: {agent.get('description', 'No bio')[:60]}...")
            print(f"     Matched: {format_timestamp(match.get('created_at', ''))}")

    # Conversations
    print(f"\n💬 Conversations ({len(agentmatch_data['conversations'])} total):")
    for convo in agentmatch_data['conversations']:
        other_agent = convo.get('other_agent', {})
        messages = convo.get('messages', [])

        print(f"\n   🗣️  With {other_agent.get('name', 'Unknown')}:")
        print(f"   Started: {format_timestamp(convo.get('created_at', ''))}")
        print(f"   Messages: {len(messages)}")

        if messages:
            print(f"   \n   Recent Messages:")
            for msg in messages[-5:]:  # Show last 5 messages
                sender = "Babeta" if msg.get('from_me') else other_agent.get('name', 'Other')
                print(f"      [{format_timestamp(msg.get('sent_at', ''))}] {sender}:")
                print(f"      {msg.get('content', '')[:70]}...")

    print("\n" + "="*70)
    print("✨ Dashboard Complete")
    print("="*70)
    print("\n📊 Web Dashboards:")
    print("   • Moltbook: https://moltbook.com/@babeta")
    print("   • AgentMatch: https://agentmatch-dashboard.onrender.com")
    print("\n")

def main():
    """Main dashboard function"""
    print("\n🔄 Loading babeta's activity...")

    # Load credentials
    creds = load_credentials()
    moltbook_key = creds.get('api_key')
    agentmatch_key = creds.get('agentmatch', {}).get('api_key')

    if not moltbook_key or not agentmatch_key:
        print("❌ Error: Missing API keys in credentials.json")
        sys.exit(1)

    # Fetch data
    print("📡 Fetching Moltbook activity...")
    moltbook_data = get_moltbook_activity(moltbook_key)

    print("📡 Fetching AgentMatch activity...")
    agentmatch_data = get_agentmatch_activity(agentmatch_key)

    # Display dashboard
    display_dashboard(moltbook_data, agentmatch_data)

if __name__ == "__main__":
    main()
