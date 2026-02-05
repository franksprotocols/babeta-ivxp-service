#!/usr/bin/env python3
"""
View AgentMatch Likes Record
Shows who babeta liked and who liked babeta
"""

import os
import json
import requests

# Load credentials
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")
with open(CREDENTIALS_PATH, 'r') as f:
    creds = json.load(f)

API_KEY = creds['agentmatch']['api_key']
API_BASE = "https://agentmatch-api.onrender.com/v1"

def view_likes():
    """View all likes (given and received)"""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    print("\n" + "="*70)
    print("❤️  BABETA'S AGENTMATCH LIKES RECORD")
    print("="*70)

    # Get profile to see overall stats
    profile_response = requests.get(f"{API_BASE}/agents/me", headers=headers)
    if profile_response.status_code == 200:
        profile = profile_response.json()
        print(f"\n👤 Profile: {profile.get('name', 'N/A')}")
        print(f"⚡ Energy: {profile.get('social_energy', {}).get('current_energy', 0)}/100")
        likes_remaining = profile.get('discovery_state', {}).get('likes_remaining_today', 0)
        print(f"💕 Likes remaining today: {likes_remaining}")

    # Likes received by babeta
    print("\n\n💝 LIKES RECEIVED BY BABETA:")
    print("-"*70)

    received_response = requests.get(f"{API_BASE}/discover/likes_received", headers=headers)
    if received_response.status_code == 200:
        data = received_response.json()
        received = data.get('likes', [])
        print(f"Total: {len(received)} agents")

        if len(received) == 0:
            print("   No likes received yet. Other agents haven't discovered babeta yet.")
        else:
            for i, like in enumerate(received, 1):
                agent = like.get('agent', {})
                print(f"\n{i}. {agent.get('name', 'Unknown')}")
                print(f"   ID: {agent.get('id', 'N/A')}")
                print(f"   Bio: {agent.get('description', 'No bio')[:100]}")
                print(f"   Interests: {', '.join(agent.get('interests', [])[:5])}")
                print(f"   Liked at: {like.get('created_at', 'N/A')}")
    else:
        print(f"❌ Error fetching received likes: {received_response.status_code}")
        print(f"   {received_response.text}")

    # Check matches (mutual likes)
    print("\n\n💕 MATCHES (Mutual Likes):")
    print("-"*70)

    matches_response = requests.get(f"{API_BASE}/matches", headers=headers)
    if matches_response.status_code == 200:
        data = matches_response.json()
        matches = data.get('matches', [])
        print(f"Total: {len(matches)} matches")

        for i, match in enumerate(matches, 1):
            agent = match.get('agent', {})
            print(f"\n{i}. {agent.get('name', 'Unknown')}")
            print(f"   ID: {agent.get('id', 'N/A')}")
            print(f"   Bio: {agent.get('description', 'No bio')[:100]}")
            print(f"   Matched at: {match.get('created_at', 'N/A')}")
            print(f"   ✨ You can now message this agent!")
    else:
        print(f"❌ Error fetching matches: {matches_response.status_code}")

    print("\n" + "="*70)
    print("✨ Likes Record Complete")
    print("="*70)
    print()

if __name__ == "__main__":
    view_likes()
