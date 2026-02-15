#!/bin/bash

# ================================================
# Quick Fix for 502 Bad Gateway on d23.ai
# ================================================

echo "🔧 Quick Fix for 502 Bad Gateway"
echo "=================================="
echo ""
echo "⚠️  This script shows you the commands to run ON YOUR PRODUCTION SERVER"
echo "    You need to SSH into your server first!"
echo ""
echo "SSH Command (replace with your actual server):"
echo "  ssh user@your-server-ip"
echo ""
echo "=================================="
echo ""

cat << 'EOF'

# Once connected to your production server, run these commands:

# Step 1: Navigate to your D23Web directory
cd /path/to/D23Web
# (Update the path above to your actual deployment path)

# Step 2: Check if PM2 is managing the app
pm2 list

# Step 3: Restart the app
pm2 restart d23web
# (Replace 'd23web' with your actual app name from pm2 list)

# If app is NOT in PM2 list, start it:
pm2 start npm --name "d23web" -- start
pm2 save

# Step 4: Check logs
pm2 logs d23web --lines 50

# Step 5: Verify it's running
curl http://localhost:3000
# (Should return HTML, not connection error)

# Step 6: Test the website
curl https://d23.ai
# (Should return HTML, not 502 error)

# Step 7: Check nginx (optional)
sudo nginx -t
sudo systemctl status nginx

EOF

echo ""
echo "=================================="
echo "📝 Alternative: If you don't use PM2"
echo "=================================="
echo ""

cat << 'EOF'

# If using systemd:
sudo systemctl restart d23web
sudo systemctl status d23web

# If running manually:
cd /path/to/D23Web
npm run build
PORT=3000 npm start

# Or run in background:
PORT=3000 nohup npm start > output.log 2>&1 &

EOF

echo ""
echo "=================================="
echo "✅ After running commands"
echo "=================================="
echo ""
echo "Visit https://d23.ai in your browser"
echo "If still showing 502, check:"
echo "  - pm2 logs d23web"
echo "  - sudo journalctl -u nginx -n 50"
echo ""
echo "📖 Full documentation: FIX_PRODUCTION_502.md"
echo ""
