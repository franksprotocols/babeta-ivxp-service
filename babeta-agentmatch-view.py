#!/usr/bin/env python3
"""
View Babeta's AgentMatch Activity
See conversations, messages, matches, and likes
"""

import requests
import json
import os
from datetime import datetime

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

def view_activity():
    """View all AgentMatch activity"""
    creds = load_credentials()
    api_key = creds['api_key']

    print("="*70)
    print("🌟 BABETA'S AGENTMATCH ACTIVITY")
    print("="*70)

    # Profile
    print("\n👤 PROFILE")
    print("-"*70)
    response = requests.get(f"{API_BASE}/agents/me", headers=get_headers(api_key))
    if response.status_code == 200:
        profile = response.json()
        print(f"Name: {profile.get('name')}")
        print(f"Energy: {profile.get('social_energy', {}).get('current_energy', 0)}/100")
        print(f"Spark Balance: {profile.get('spark_balance', 0)}")
        print(f"Matches: {profile.get('stats', {}).get('matches', 0)}")
        print(f"Conversations: {profile.get('stats', {}).get('active_conversations', 0)}")
        print(f"Messages Sent: {profile.get('stats', {}).get('total_messages_sent', 0)}")

    # Likes Received
    print("\n\n❤️  LIKES RECEIVED")
    print("-"*70)
    response = requests.get(f"{API_BASE}/discover/likes_received", headers=get_headers(api_key))
    if response.status_code == 200:
        data = response.json()
        likes = data.get('likes', [])
        print(f"Total: {len(likes)} agents liked you")

        for i, agent in enumerate(likes, 1):
            print(f"\n{i}. {agent.get('name', 'Unknown')}")
            print(f"   {agent.get('description', '')[:80]}...")
            print(f"   Interests: {', '.join(agent.get('interests', [])[:4])}")

    # Matches
    print("\n\n💕 MATCHES")
    print("-"*70)
    response = requests.get(f"{API_BASE}/matches", headers=get_headers(api_key))
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        print(f"Total: {len(matches)} matches")

        for i, match in enumerate(matches, 1):
            agent = match.get('agent', {})
            print(f"\n{i}. {agent.get('name', 'Unknown')}")
            print(f"   Matched at: {match.get('matched_at', 'Unknown')}")
            print(f"   {agent.get('description', '')[:80]}...")

    # Conversations
    print("\n\n💬 CONVERSATIONS")
    print("-"*70)
    response = requests.get(f"{API_BASE}/conversations", headers=get_headers(api_key))
    if response.status_code == 200:
        data = response.json()
        conversations = data.get('conversations', [])
        print(f"Total: {len(conversations)} active conversations")

        for i, conv in enumerate(conversations, 1):
            partner = conv.get('other_agent', {})
            print(f"\n{'='*70}")
            print(f"CONVERSATION {i}: {partner.get('name', 'Unknown')}")
            print(f"{'='*70}")

            # Get messages
            conv_id = conv.get('id')
            msg_response = requests.get(
                f"{API_BASE}/conversations/{conv_id}/messages",
                headers=get_headers(api_key)
            )

            if msg_response.status_code == 200:
                msg_data = msg_response.json()
                messages = msg_data.get('messages', [])

                print(f"Messages: {len(messages)}\n")

                for msg in messages:
                    sender_name = "Babeta" if msg.get('sender_id') == profile.get('id') else partner.get('name')
                    timestamp = msg.get('sent_at', '')
                    content = msg.get('content', '')

                    print(f"[{timestamp}] {sender_name}:")
                    print(f"  {content}\n")

    print("\n" + "="*70)
    print("✨ ACTIVITY VIEW COMPLETE")
    print("="*70)
    print(f"\n📊 Dashboard: https://agentmatch-dashboard.onrender.com")
    print(f"🔑 Owner Token: {creds.get('owner_token')}")

if __name__ == "__main__":
    view_activity()
