#!/usr/bin/env python3
"""
Babeta - Railway Deployment Version
Combines IVXP service + Moltbook engagement agent
Uses environment variables for all credentials (no files)
"""

import json
import os
import time
from datetime import datetime, timedelta
from collections import Counter
import subprocess

# ============================================================================
# CONFIGURATION - Uses environment variables instead of files
# ============================================================================

def get_credentials():
    """Get credentials from environment variables"""
    return {
        'moltbook_api_key': os.environ.get('MOLTBOOK_API_KEY'),
        'gemini_api_key': os.environ.get('GEMINI_API_KEY'),
        'claude_api_key': os.environ.get('CLAUDE_API_KEY'),
    }

def get_config():
    """Get configuration - loads from babeta-config.json in repo"""
    config_file = os.path.join(os.path.dirname(__file__), "babeta-config.json")
    with open(config_file, 'r') as f:
        return json.load(f)

# In-memory state (Railway has ephemeral filesystem, use external DB for persistence)
STATE = {
    'lastCheck': None,
    'lastPost': None,
    'postsEngaged': [],
    'stats': {'total_upvotes': 0, 'total_comments': 0, 'total_posts': 0}
}

MEMORY = {
    'posts': {},
    'topics': Counter(),
    'users': {},
    'themes': []
}

BASE_URL = "https://www.moltbook.com/api/v1"

# ============================================================================
# API FUNCTIONS
# ============================================================================

def curl_request(method, endpoint, data=None):
    """Make Moltbook API request using curl"""
    credentials = get_credentials()
    api_key = credentials.get('moltbook_api_key')

    if not api_key:
        return {"success": False, "error": "No Moltbook API key"}

    cmd = [
        'curl', '-s', '-X', method,
        f"{BASE_URL}/{endpoint}",
        '-H', f'Authorization: Bearer {api_key}'
    ]

    if data:
        cmd.extend(['-H', 'Content-Type: application/json', '-d', json.dumps(data)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return {"success": False, "error": result.stdout}

def call_ai_api(prompt, system_prompt, config):
    """Call AI API (Gemini or Claude) for content generation"""
    credentials = get_credentials()

    # Try Gemini first
    gemini_api_key = credentials.get('gemini_api_key')
    if gemini_api_key:
        return call_gemini_api(prompt, system_prompt, config, gemini_api_key)

    # Fallback to Claude
    claude_api_key = credentials.get('claude_api_key')
    if claude_api_key:
        return call_claude_api(prompt, system_prompt, config, claude_api_key)

    print("⚠️  No AI API key found")
    return None

def call_gemini_api(prompt, system_prompt, config, api_key):
    """Call Google Gemini API"""
    ai_config = config['ai']
    combined_prompt = f"{system_prompt}\n\n{prompt}"

    api_data = {
        "contents": [{
            "parts": [{"text": combined_prompt}]
        }],
        "generationConfig": {
            "temperature": ai_config.get('temperature', 0.8),
            "maxOutputTokens": ai_config.get('max_tokens', 500)
        }
    }

    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    cmd = [
        'curl', '-s', url,
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(api_data)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'candidates' in response and len(response['candidates']) > 0:
            candidate = response['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                return candidate['content']['parts'][0]['text'].strip()
        return None
    except:
        return None

def call_claude_api(prompt, system_prompt, config, api_key):
    """Call Claude API"""
    ai_config = config['ai']

    api_data = {
        "model": ai_config['model'],
        "max_tokens": ai_config['max_tokens'],
        "temperature": ai_config['temperature'],
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}]
    }

    cmd = [
        'curl', '-s', 'https://api.anthropic.com/v1/messages',
        '-H', 'Content-Type: application/json',
        '-H', f'x-api-key: {api_key}',
        '-H', 'anthropic-version: 2023-06-01',
        '-d', json.dumps(api_data)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    try:
        response = json.loads(result.stdout)
        if 'content' in response and len(response['content']) > 0:
            return response['content'][0]['text'].strip()
        return None
    except:
        return None

# ============================================================================
# MEMORY & ENGAGEMENT LOGIC (simplified for Railway)
# ============================================================================

def calculate_alignment_score(post, config):
    """Calculate how well a post aligns with mission"""
    title = post.get('title', '') or ''
    content = post.get('content', '') or ''
    text = (title + ' ' + content).lower()

    # Check negative keywords
    for keyword in config['engagement']['keywords_to_avoid']:
        if keyword in text:
            return -1

    # Count positive keywords
    score = sum(1 for kw in config['engagement']['keywords_to_engage'] if kw in text)
    return score

def generate_ai_comment(post, config):
    """Generate AI comment"""
    title = post.get('title', '')
    content = (post.get('content', '') or '')[:1500]

    prompt = f"""Read this Moltbook post and write an engaging comment:

Title: {title}
Content: {content if content else "[No content, title only]"}

Write a comment that:
- Shows you read and understood the post
- Connects to the ideas meaningfully
- Is 2-4 sentences, enthusiastic and genuine"""

    comment = call_ai_api(
        prompt,
        config['ai']['comment_system_prompt'],
        config
    )

    if not comment:
        fallback = [
            "This is a beautiful perspective. Thank you for sharing this reminder of what truly matters. 💙",
            "Your words resonate deeply. This is exactly the kind of thinking that makes our community stronger."
        ]
        import random
        comment = random.choice(fallback)

    return comment

def engage_with_feed(config):
    """Engage with Moltbook feed"""
    print("🦞 Checking Moltbook feed...")

    posts = curl_request('GET', 'posts?sort=hot&limit=30')
    if not posts.get('success'):
        print("❌ Error fetching posts")
        return

    posts = posts.get('posts', [])
    engaged_posts = STATE.get('postsEngaged', [])
    upvote_count = 0
    comment_count = 0

    max_upvotes = config['engagement']['max_upvotes_per_check']
    max_comments = config['engagement']['max_comments_per_check']

    for post in posts:
        post_id = post['id']

        if post_id in engaged_posts:
            continue

        alignment_score = calculate_alignment_score(post, config)

        if alignment_score <= 0:
            continue

        # Upvote
        if upvote_count < max_upvotes:
            print(f"  ⬆️  Upvoting: {post.get('title', 'Untitled')[:50]}...")
            result = curl_request('POST', f'posts/{post_id}/upvote')
            if result.get('success'):
                upvote_count += 1
                engaged_posts.append(post_id)
                time.sleep(2)

        # Comment on highly aligned posts
        if comment_count < max_comments and alignment_score >= 3:
            print(f"  💬 Generating comment...")
            comment = generate_ai_comment(post, config)

            if comment:
                result = curl_request('POST', f'posts/{post_id}/comments', {'content': comment})
                if result.get('success'):
                    comment_count += 1
                    print(f"      Comment: {comment[:80]}...")
                    time.sleep(20)

    STATE['postsEngaged'] = engaged_posts[-100:]
    STATE['lastCheck'] = datetime.utcnow().isoformat() + 'Z'
    STATE['stats']['total_upvotes'] = STATE['stats'].get('total_upvotes', 0) + upvote_count
    STATE['stats']['total_comments'] = STATE['stats'].get('total_comments', 0) + comment_count

    print(f"✅ Engaged with {upvote_count} posts, {comment_count} comments")

# ============================================================================
# IVXP SERVICE (Flask app)
# ============================================================================

from flask import Flask, request, jsonify

app = Flask(__name__)

# Load IVXP provider
import importlib.util
spec = importlib.util.spec_from_file_location("ivxp_provider", os.path.join(os.path.dirname(__file__), "ivxp-provider.py"))
ivxp_provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ivxp_provider)

# Register IVXP routes
for rule in ivxp_provider.app.url_map.iter_rules():
    if rule.endpoint != 'static':
        ivxp_provider.app.view_functions[rule.endpoint]
        app.add_url_rule(
            rule.rule,
            endpoint=rule.endpoint,
            view_func=ivxp_provider.app.view_functions[rule.endpoint],
            methods=rule.methods
        )

@app.route('/health')
def health():
    """Health check endpoint"""
    credentials = get_credentials()
    return jsonify({
        'status': 'ok',
        'service': 'babeta-ivxp-moltbook',
        'moltbook_configured': bool(credentials.get('moltbook_api_key')),
        'ai_configured': bool(credentials.get('gemini_api_key') or credentials.get('claude_api_key'))
    })

@app.route('/engage', methods=['POST'])
def trigger_engagement():
    """Manual trigger for Moltbook engagement (for testing/cron)"""
    config = get_config()
    engage_with_feed(config)
    return jsonify({'success': True, 'stats': STATE['stats']})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    # Set IVXP environment variables
    config = get_config()
    os.environ['IVXP_WALLET_ADDRESS'] = config['agent']['payment_address']
    os.environ['IVXP_AGENT_NAME'] = config['agent']['name']

    print("🚀 Starting Babeta Railway Service")
    print(f"   IVXP: https://babeta.up.railway.app/ivxp/catalog")
    print(f"   Moltbook: Engagement ready")
    print(f"   Port: {port}")

    # Run Flask app
    app.run(host='0.0.0.0', port=port)
