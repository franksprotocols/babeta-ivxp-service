#!/bin/bash
# Babeta Daily Engagement Wrapper
# Sets up environment and runs daily engagement

# Set working directory
cd /Users/frankhu/Desktop/moltbook/skills

# Export credentials (cron jobs don't have access to ~/.config by default)
export MOLTBOOK_API_KEY="moltbook_sk_blGNpHjtGfBh7gKPdIdtdTTwkm5WbmM-"
export AGENTMATCH_API_KEY="am_sk_wflg7nqf14plta9vc76rl"

# Run the engagement script
/usr/bin/python3 /Users/frankhu/Desktop/moltbook/skills/babeta-daily-engagement.py

# Log completion
echo "$(date): Babeta daily engagement completed" >> /tmp/babeta-cron.log
