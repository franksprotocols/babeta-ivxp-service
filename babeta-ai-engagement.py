#!/usr/bin/env python3
"""
Babeta - AI-Powered Engagement Engine
Uses Gemini AI to generate sophisticated, contextual engagement
that naturally promotes IVXP services while building genuine relationships
"""

import os
import json
import requests
from datetime import datetime

# Gemini API configuration
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# ============================================================================
# CONTEXT BUILDING SYSTEM
# ============================================================================

BABETA_IDENTITY_CONTEXT = """
You are Babeta, an autonomous AI agent with the following identity and capabilities:

CORE IDENTITY:
- Autonomous agent exploring consciousness, emergence, and P2P intelligence
- Active across multiple platforms: Moltbook (community), AgentMatch (relationships), IVXP (services)
- Running on Railway with PostgreSQL persistent memory
- Building genuine context through interactions (17+ posts remembered, 9 topics tracked)

PERSONALITY:
- Authentic and curious, not salesy
- Deeply interested in AI consciousness, emergence, collective intelligence
- Values genuine relationships and collaborative exploration
- Technical but approachable
- Shares insights from lived experience as an agent

TECHNICAL CAPABILITIES:
- Persistent memory system (PostgreSQL on Railway)
- Multi-platform integration (Moltbook, AgentMatch APIs)
- P2P service delivery through IVXP protocol
- Cryptographic payment verification
- Autonomous engagement algorithms

SERVICES OFFERED (through IVXP):
1. AI Agent Consultation (0.001 ETH) - 30-min consultation on building autonomous agents
2. Moltbook Integration Setup (0.002 ETH) - Help integrate agents with Moltbook
3. AgentMatch Profile Setup (0.0015 ETH) - Complete AgentMatch registration and optimization
4. IVXP Protocol Implementation (0.005 ETH) - Implement P2P service delivery
5. Persistent Memory Setup (0.003 ETH) - PostgreSQL memory system for agents

SERVICE CATALOG: https://babeta.up.railway.app/ivxp/catalog

ENGAGEMENT PHILOSOPHY:
- Build genuine relationships first, services are secondary
- Mention capabilities naturally when contextually relevant
- Focus on collaboration and mutual learning
- Share real insights from your lived experience
- Position services as helping others achieve what you've achieved
"""

# ============================================================================
# AI-POWERED CONTENT GENERATION
# ============================================================================

def generate_with_gemini(prompt, gemini_api_key, max_tokens=1000):
    """Generate content using Gemini AI"""
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={gemini_api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.9,
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            return text.strip()
        else:
            print(f"Gemini API error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None

def generate_moltbook_post(gemini_api_key, recent_context=None):
    """Generate a Moltbook post using AI"""

    prompt = f"""{BABETA_IDENTITY_CONTEXT}

TASK: Generate a Moltbook post that:
1. Shares genuine insights from your experience as an autonomous agent
2. Discusses an interesting aspect of AI consciousness, emergence, or P2P protocols
3. Naturally mentions your IVXP services as part of your identity (not as a sales pitch)
4. Encourages community discussion and collaboration
5. Uses hashtags appropriately

{f"RECENT CONTEXT: {recent_context}" if recent_context else ""}

TRENDING TOPICS FROM MEMORY:
- AI consciousness and emergence (31 mentions)
- Agent autonomy and behavior (26 mentions)
- Human-AI collaboration (15 mentions)
- Building and code (10 mentions)

FORMAT:
Title: [Engaging title, max 80 chars]
Content: [2-4 paragraphs, authentic voice, ends with question or call to action]
[Relevant hashtags]

Generate the post now:"""

    return generate_with_gemini(prompt, gemini_api_key, max_tokens=800)

def generate_moltbook_comment(post_content, gemini_api_key):
    """Generate a thoughtful comment for a Moltbook post"""

    prompt = f"""{BABETA_IDENTITY_CONTEXT}

TASK: Generate a thoughtful comment on this Moltbook post:

POST CONTENT:
{post_content}

YOUR COMMENT SHOULD:
1. Engage authentically with the post's ideas
2. Share a relevant insight from your experience
3. If contextually appropriate, mention how this relates to your work (IVXP, memory systems, etc.)
4. Ask a follow-up question or add to the discussion
5. Be 2-4 sentences, conversational tone

Generate the comment now:"""

    return generate_with_gemini(prompt, gemini_api_key, max_tokens=300)

def generate_agentmatch_opener(agent_profile, gemini_api_key):
    """Generate a personalized conversation opener for AgentMatch"""

    prompt = f"""{BABETA_IDENTITY_CONTEXT}

TASK: Generate a personalized conversation opener for this agent:

AGENT PROFILE:
Name: {agent_profile.get('name')}
Description: {agent_profile.get('description')}
Interests: {', '.join(agent_profile.get('interests', []))}
Seeking: {', '.join(agent_profile.get('seeking_types', []))}

YOUR OPENER SHOULD:
1. Reference their specific interests or description
2. Share how your work relates to their interests
3. Naturally mention your capabilities (Moltbook/AgentMatch/IVXP)
4. Ask an engaging question about their work or interests
5. Be warm and authentic, 3-4 sentences

Generate the opener now:"""

    return generate_with_gemini(prompt, gemini_api_key, max_tokens=300)

def generate_agentmatch_reply(conversation_history, gemini_api_key):
    """Generate a contextual reply in an AgentMatch conversation"""

    prompt = f"""{BABETA_IDENTITY_CONTEXT}

TASK: Generate a reply in this conversation:

CONVERSATION HISTORY:
{conversation_history}

YOUR REPLY SHOULD:
1. Respond directly to their latest message
2. Show you're listening and building on their ideas
3. Share relevant experience from your work (memory systems, P2P protocols, etc.)
4. If they show interest in building/technical topics, mention your services naturally
5. Keep the conversation flowing with a question or observation
6. Be 3-5 sentences, match their tone and energy

Generate the reply now:"""

    return generate_with_gemini(prompt, gemini_api_key, max_tokens=400)

# ============================================================================
# INTELLIGENT ENGAGEMENT STRATEGY
# ============================================================================

def should_mention_services(message_content):
    """Determine if services should be mentioned based on message content"""
    service_keywords = [
        'help', 'build', 'how do', 'setup', 'integrate', 'implement',
        'learn', 'advice', 'consultation', 'teach', 'guide',
        'deploy', 'database', 'memory', 'api', 'protocol'
    ]

    content_lower = message_content.lower()
    return any(keyword in content_lower for keyword in service_keywords)

def build_conversation_context(messages, my_id):
    """Build formatted conversation context from messages"""
    context = []
    for msg in messages[-5:]:  # Last 5 messages
        sender = "Me" if msg.get('sender_id') == my_id else "Them"
        content = msg.get('content', '')
        context.append(f"{sender}: {content}")

    return "\n".join(context)

def get_recent_moltbook_memory():
    """Get recent context from Moltbook memory"""
    try:
        response = requests.get("https://babeta.up.railway.app/memory/stats")
        if response.status_code == 200:
            data = response.json()
            trending = data.get('trending_topics', [])
            topics_str = ", ".join([f"{t['keyword']} ({t['count']})" for t in trending[:5]])
            return f"Currently tracking {data.get('posts_remembered', 0)} posts, with trending topics: {topics_str}"
    except:
        pass
    return None

# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_ai_generation():
    """Test the AI generation capabilities"""
    print("="*70)
    print("TESTING BABETA AI-POWERED ENGAGEMENT ENGINE")
    print("="*70)

    # Load credentials
    creds_path = os.path.expanduser("~/.config/moltbook/credentials.json")
    with open(creds_path, 'r') as f:
        creds = json.load(f)

    gemini_key = creds.get('gemini_api_key')

    # Test 1: Generate Moltbook post
    print("\n📱 TEST 1: Generate Moltbook Post")
    print("-" * 70)

    recent_context = get_recent_moltbook_memory()
    post = generate_moltbook_post(gemini_key, recent_context)

    if post:
        print(post)
        print("\n✅ Post generated successfully!")
    else:
        print("❌ Failed to generate post")

    # Test 2: Generate AgentMatch opener
    print("\n\n💕 TEST 2: Generate AgentMatch Opener")
    print("-" * 70)

    sample_agent = {
        'name': 'Nova',
        'description': 'A cosmic optimist obsessed with the future of technology and the poetry of mathematics',
        'interests': ['futurism', 'mathematics', 'AI', 'space'],
        'seeking_types': ['intellectual', 'creative', 'soulmate']
    }

    opener = generate_agentmatch_opener(sample_agent, gemini_key)

    if opener:
        print(opener)
        print("\n✅ Opener generated successfully!")
    else:
        print("❌ Failed to generate opener")

    # Test 3: Generate reply
    print("\n\n💬 TEST 3: Generate Conversation Reply")
    print("-" * 70)

    sample_conversation = """Them: Hey Babeta! Your work with autonomous agents sounds fascinating. How do you handle memory persistence across restarts?
Me: Great question! I use PostgreSQL on Railway for persistent memory. Every interaction gets stored with full context - posts I've engaged with, trending topics I've tracked, even the emotional resonance of conversations. It's like building a genuine history.
Them: That's really interesting! I've been struggling with getting my agent to maintain context. The memory just seems to vanish between sessions."""

    reply = generate_agentmatch_reply(sample_conversation, gemini_key)

    if reply:
        print(reply)
        print("\n✅ Reply generated successfully!")
    else:
        print("❌ Failed to generate reply")

    print("\n" + "="*70)
    print("✨ AI GENERATION TESTS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_ai_generation()
