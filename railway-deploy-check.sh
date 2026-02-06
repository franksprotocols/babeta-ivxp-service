#!/bin/bash
# Railway Quick Deploy Test
# Tests if babeta service is ready to deploy

echo "🚂 RAILWAY DEPLOYMENT CHECKLIST"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "babeta-ivxp-service.py" ]; then
    echo "❌ ERROR: babeta-ivxp-service.py not found"
    echo "   Run this script from /Users/frankhu/Desktop/moltbook/skills"
    exit 1
fi

echo "✅ Found babeta-ivxp-service.py"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  WARNING: requirements.txt not found"
    echo "   Creating requirements.txt..."
    cat > requirements.txt <<EOF
flask==3.0.0
psycopg2-binary==2.9.9
requests==2.31.0
EOF
    echo "✅ Created requirements.txt"
else
    echo "✅ Found requirements.txt"
fi

# Check if Procfile exists
if [ ! -f "Procfile" ]; then
    echo "⚠️  WARNING: Procfile not found"
    echo "   Creating Procfile..."
    echo "web: python3 babeta-ivxp-service.py" > Procfile
    echo "✅ Created Procfile"
else
    echo "✅ Found Procfile"
fi

# Check if babeta-config.json exists
if [ ! -f "babeta-config.json" ]; then
    echo "❌ ERROR: babeta-config.json not found"
    echo "   This file is required for configuration"
    exit 1
fi

echo "✅ Found babeta-config.json"

# Show git status
echo ""
echo "📊 Git Status:"
git status --short

# Check if changes need to be committed
if [[ -n $(git status --porcelain) ]]; then
    echo ""
    echo "📝 Uncommitted changes detected. Committing..."
    git add requirements.txt Procfile 2>/dev/null
    git commit -m "Add Railway deployment files (requirements.txt, Procfile)" 2>/dev/null
    echo "✅ Changes committed"
fi

# Push to GitHub
echo ""
echo "⬆️  Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Pushed to GitHub successfully"
else
    echo "❌ Git push failed"
    exit 1
fi

echo ""
echo "================================"
echo "✅ REPOSITORY READY FOR RAILWAY"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Go to https://railway.app/dashboard"
echo "2. Find 'babeta-ivxp-service' project"
echo "3. Click on the service"
echo "4. Go to Settings → Service"
echo "5. Verify GitHub repo: franksprotocols/babeta-ivxp-service"
echo "6. Check Start Command: python3 babeta-ivxp-service.py"
echo "7. Verify environment variables are set"
echo "8. Click 'Redeploy' or wait for auto-deploy"
echo ""
echo "Test deployment:"
echo "curl https://babeta-ivxp-service-production.up.railway.app/health"
echo ""
