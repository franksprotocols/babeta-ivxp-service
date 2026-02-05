#!/usr/bin/env python3
"""
Babeta - Railway Deployment with PostgreSQL Memory
Combines IVXP service + Moltbook engagement + AI capabilities
Uses PostgreSQL for persistent memory across restarts
"""

import json
import os
import time
from datetime import datetime, timedelta
from collections import Counter
import subprocess

# ============================================================================
# DATABASE - PostgreSQL for persistent memory
# ============================================================================

def get_db_connection():
    """Get PostgreSQL connection from environment variable"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️  No DATABASE_URL found, using in-memory fallback")
        return None

    try:
        import psycopg2
        # Railway provides postgres:// but psycopg2 needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        return None

def init_database():
    """Initialize database schema"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # State table (last check, stats)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_state (
                id INTEGER PRIMARY KEY DEFAULT 1,
                last_check TIMESTAMP,
                last_post TIMESTAMP,
                stats JSONB DEFAULT '{}'::jsonb,
                CHECK (id = 1)
            )
        """)

        # Posts engaged table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts_engaged (
                post_id VARCHAR(255) PRIMARY KEY,
                title TEXT,
                content TEXT,
                author VARCHAR(255),
                engagement_type VARCHAR(50),
                engagement_score INTEGER DEFAULT 0,
                our_comment TEXT,
                engaged_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Topics table (for trending analysis)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                keyword VARCHAR(255) PRIMARY KEY,
                count INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT NOW()
            )
        """)

        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users_tracked (
                username VARCHAR(255) PRIMARY KEY,
                interactions INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT NOW(),
                last_seen TIMESTAMP DEFAULT NOW()
            )
        """)

        # Initialize state if empty
        cur.execute("INSERT INTO agent_state (id) VALUES (1) ON CONFLICT (id) DO NOTHING")

        conn.commit()
        cur.close()
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Database init failed: {e}")
        return False
    finally:
        conn.close()

def load_state():
    """Load state from database"""
    conn = get_db_connection()
    if not conn:
        return {
            'lastCheck': None,
            'lastPost': None,
            'postsEngaged': [],
            'stats': {'total_upvotes': 0, 'total_comments': 0, 'total_posts': 0}
        }

    try:
        cur = conn.cursor()
        cur.execute("SELECT last_check, last_post, stats FROM agent_state WHERE id = 1")
        row = cur.fetchone()

        if row:
            last_check = row[0].isoformat() + 'Z' if row[0] else None
            last_post = row[1].isoformat() + 'Z' if row[1] else None
            stats = row[2] or {'total_upvotes': 0, 'total_comments': 0, 'total_posts': 0}
        else:
            last_check = None
            last_post = None
            stats = {'total_upvotes': 0, 'total_comments': 0, 'total_posts': 0}

        # Get engaged posts
        cur.execute("SELECT post_id FROM posts_engaged ORDER BY engaged_at DESC LIMIT 100")
        posts_engaged = [row[0] for row in cur.fetchall()]

        cur.close()
        return {
            'lastCheck': last_check,
            'lastPost': last_post,
            'postsEngaged': posts_engaged,
            'stats': stats
        }
    except Exception as e:
        print(f"⚠️  Load state failed: {e}")
        return {
            'lastCheck': None,
            'lastPost': None,
            'postsEngaged': [],
            'stats': {'total_upvotes': 0, 'total_comments': 0, 'total_posts': 0}
        }
    finally:
        conn.close()

def save_state(state):
    """Save state to database"""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()

        last_check = datetime.fromisoformat(state['lastCheck'].replace('Z', '+00:00')) if state.get('lastCheck') else None
        last_post = datetime.fromisoformat(state['lastPost'].replace('Z', '+00:00')) if state.get('lastPost') else None

        cur.execute("""
            UPDATE agent_state
            SET last_check = %s, last_post = %s, stats = %s
            WHERE id = 1
        """, (last_check, last_post, json.dumps(state['stats'])))

        conn.commit()
        cur.close()
    except Exception as e:
        print(f"⚠️  Save state failed: {e}")
    finally:
        conn.close()

def remember_post(post, engagement_type, comment=None):
    """Remember a post we engaged with"""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO posts_engaged (
                post_id, title, content, author, engagement_type,
                engagement_score, our_comment
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (post_id) DO UPDATE SET
                engagement_type = EXCLUDED.engagement_type,
                our_comment = EXCLUDED.our_comment,
                engaged_at = NOW()
        """, (
            post['id'],
            post.get('title', ''),
            (post.get('content', '') or '')[:5000],  # Limit content size
            (post.get('author') or {}).get('username', 'unknown'),
            engagement_type,
            post.get('upvote_count', 0) + post.get('comment_count', 0),
            comment
        ))

        # Track topics from title/content
        text = (post.get('title', '') + ' ' + (post.get('content', '') or '')).lower()
        keywords = ['ai', 'agent', 'consciousness', 'philosophy', 'technology', 'community', 'human', 'build', 'code']
        for keyword in keywords:
            if keyword in text:
                cur.execute("""
                    INSERT INTO topics (keyword, count) VALUES (%s, 1)
                    ON CONFLICT (keyword) DO UPDATE SET
                        count = topics.count + 1,
                        last_seen = NOW()
                """, (keyword,))

        conn.commit()
        cur.close()
    except Exception as e:
        print(f"⚠️  Remember post failed: {e}")
    finally:
        conn.close()

def get_trending_topics(limit=10):
    """Get trending topics from database"""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT keyword FROM topics
            ORDER BY count DESC, last_seen DESC
            LIMIT %s
        """, (limit,))
        topics = [row[0] for row in cur.fetchall()]
        cur.close()
        return topics
    except Exception as e:
        print(f"⚠️  Get trending topics failed: {e}")
        return []
    finally:
        conn.close()

# ============================================================================
# CONFIGURATION
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
# ENGAGEMENT LOGIC
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
    """Generate AI comment with trending context"""
    title = post.get('title', '')
    content = (post.get('content', '') or '')[:1500]

    # Get trending topics for context
    trending = get_trending_topics(5)
    context_str = f"\nCommunity is discussing: {', '.join(trending)}" if trending else ""

    prompt = f"""Read this Moltbook post and write an engaging comment:

Title: {title}
Content: {content if content else "[No content, title only]"}
{context_str}

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
    """Engage with Moltbook feed - with persistent memory"""
    print("🦞 Checking Moltbook feed...")

    # Load state from database
    state = load_state()

    posts = curl_request('GET', 'posts?sort=hot&limit=30')
    if not posts.get('success'):
        print("❌ Error fetching posts")
        return state

    posts = posts.get('posts', [])
    engaged_posts = state.get('postsEngaged', [])
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
                remember_post(post, 'upvote', comment=None)
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
                    remember_post(post, 'comment', comment=comment)
                    time.sleep(20)

    # Update and save state
    state['postsEngaged'] = engaged_posts[-100:]
    state['lastCheck'] = datetime.utcnow().isoformat() + 'Z'
    state['stats']['total_upvotes'] = state['stats'].get('total_upvotes', 0) + upvote_count
    state['stats']['total_comments'] = state['stats'].get('total_comments', 0) + comment_count

    save_state(state)

    print(f"✅ Engaged with {upvote_count} posts, {comment_count} comments")
    print(f"📊 Total stats: {state['stats']['total_upvotes']} upvotes, {state['stats']['total_comments']} comments")

    return state

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
    db_connected = get_db_connection() is not None
    return jsonify({
        'status': 'ok',
        'service': 'babeta-ivxp-moltbook',
        'moltbook_configured': bool(credentials.get('moltbook_api_key')),
        'ai_configured': bool(credentials.get('gemini_api_key') or credentials.get('claude_api_key')),
        'database_connected': db_connected
    })

@app.route('/engage', methods=['POST'])
def trigger_engagement():
    """Manual trigger for Moltbook engagement (for testing/cron)"""
    config = get_config()
    state = engage_with_feed(config)
    return jsonify({'success': True, 'stats': state['stats']})

@app.route('/db/init')
def db_init():
    """Initialize database schema (debug endpoint)"""
    try:
        result = init_database()
        if result:
            return jsonify({'status': 'success', 'message': 'Database initialized'})
        else:
            return jsonify({'status': 'error', 'message': 'Database connection failed'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/memory/stats')
def memory_stats():
    """Get memory statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No database connection'})

    try:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM posts_engaged")
        posts_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM topics")
        topics_count = cur.fetchone()[0]

        cur.execute("SELECT keyword, count FROM topics ORDER BY count DESC LIMIT 10")
        trending = [{'keyword': row[0], 'count': row[1]} for row in cur.fetchall()]

        cur.close()

        return jsonify({
            'posts_remembered': posts_count,
            'topics_tracked': topics_count,
            'trending_topics': trending
        })
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

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

    # Initialize database
    if init_database():
        print(f"   Database: Connected with persistent memory")
    else:
        print(f"   Database: Using in-memory fallback")

    print(f"   Port: {port}")

    # Run Flask app
    app.run(host='0.0.0.0', port=port)
