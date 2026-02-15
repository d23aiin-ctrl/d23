#!/bin/bash

# ===========================================
# Run D23Web Admin Dashboard on Port 5050
# ===========================================

echo "🚀 Starting D23Web Admin Dashboard on port 5050..."
echo ""

# Navigate to D23Web directory
cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start Next.js on port 5050
echo "✅ Starting server..."
echo "📊 Dashboard will be available at: http://localhost:5050"
echo "🔐 Admin Login: http://localhost:5050/admin/whatsapp"
echo ""

PORT=5050 npm run dev
