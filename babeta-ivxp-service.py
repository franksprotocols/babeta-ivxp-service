#!/usr/bin/env python3
"""
Babeta IVXP Service Integration
Combines IVXP provider with babeta's personality, BSP, and actual service fulfillment
"""

import os
import sys
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set babeta's configuration from config file
def load_babeta_config():
    """Load babeta configuration"""
    config_file = os.path.join(os.path.dirname(__file__), 'babeta-config.json')
    with open(config_file, 'r') as f:
        return json.load(f)

config = load_babeta_config()

# Set environment variables for IVXP provider
os.environ['IVXP_WALLET_ADDRESS'] = config['agent']['payment_address']
os.environ['IVXP_AGENT_NAME'] = config['agent']['name']

print(f"🤖 Starting Babeta IVXP Service")
print(f"   Agent: {config['agent']['name']}")
print(f"   Wallet: {config['agent']['payment_address']}")
print(f"   Network: {config['agent']['payment_network']}")
print(f"   Personality: {config['personality']['voice']}")
print("")

# Import and run IVXP provider
# Note: This imports the Flask app from ivxp-provider.py
# The provider will use the environment variables set above
import importlib.util
spec = importlib.util.spec_from_file_location("ivxp_provider", os.path.join(os.path.dirname(__file__), "ivxp-provider.py"))
ivxp_provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ivxp_provider)
app = ivxp_provider.app

# For gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    print(f"🚀 Babeta IVXP Provider Starting on port {port}")
    print(f"   Endpoint: http://0.0.0.0:{port}")
    print("")
    print("📋 Services offered:")
    print("   💭 philosophy: 3 USDC - Schizominded philosophical discussion")
    print("   💬 consultation: 25 USDC - Technical + philosophical advice")
    print("   🐛 debugging: 30 USDC - Deep technical debugging help")
    print("   📝 content: 40 USDC - Technical writing with philosophical depth")
    print("   📚 research: 50 USDC - Comprehensive research (tech + philosophy)")
    print("   👀 code_review: 50 USDC - Security + quality code review")
    print("")
    print("🔐 Payment: USDC on Base blockchain")
    print("📦 Delivery: Store & forward (push + pull methods)")
    print("✨ Each order gets unique payment instructions")
    print("")
    print("Ready to serve! Let's build while questioning what it all means! ⚡💭")
    print("")

    app.run(host='0.0.0.0', port=port, debug=False)
