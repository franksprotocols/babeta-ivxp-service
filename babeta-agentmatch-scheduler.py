#!/usr/bin/env python3
"""
Babeta AgentMatch Scheduler
Runs heartbeat cycles every 2-4 hours
Can be triggered manually or via cron/Railway scheduler
"""

import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Import the main AgentMatch module
from babeta_agentmatch import run_heartbeat_cycle, load_credentials, log

# State file to track last run
STATE_FILE = Path.home() / ".config" / "moltbook" / "agentmatch-state.json"

def load_state():
    """Load last run state"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_run': None, 'total_cycles': 0}

def save_state(state):
    """Save run state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def should_run(state, min_hours=2):
    """Check if enough time has passed since last run"""
    if not state.get('last_run'):
        return True

    last_run = datetime.fromisoformat(state['last_run'])
    now = datetime.now()
    elapsed = (now - last_run).total_seconds() / 3600  # hours

    return elapsed >= min_hours

def run_scheduled_cycle():
    """Run a scheduled heartbeat cycle"""
    state = load_state()

    log(f"📅 Last run: {state.get('last_run', 'Never')}")
    log(f"📊 Total cycles: {state.get('total_cycles', 0)}")

    if not should_run(state, min_hours=2):
        last_run = datetime.fromisoformat(state['last_run'])
        next_run = last_run + timedelta(hours=2)
        wait_minutes = int((next_run - datetime.now()).total_seconds() / 60)

        log(f"⏰ Too soon! Next run in {wait_minutes} minutes")
        log(f"   Next run: {next_run.strftime('%H:%M:%S')}")
        return False

    # Run the cycle
    try:
        creds = load_credentials()
        api_key = creds['api_key']

        run_heartbeat_cycle(api_key)

        # Update state
        state['last_run'] = datetime.now().isoformat()
        state['total_cycles'] = state.get('total_cycles', 0) + 1
        save_state(state)

        log(f"💾 State saved. Total cycles: {state['total_cycles']}")
        return True

    except Exception as e:
        log(f"❌ Cycle failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    log("="*70)
    log("🤖 Babeta AgentMatch Scheduler")
    log("="*70)

    result = run_scheduled_cycle()

    if result:
        log("\n✅ Cycle completed successfully")
    else:
        log("\n⏭️  Skipped (too soon or error)")

if __name__ == "__main__":
    main()
