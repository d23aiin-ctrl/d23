#!/bin/bash

# ===========================================
# Start D23Web QA with Production API
# ===========================================

set -e

echo "🚀 Starting D23Web on Port 5050 (QA Mode)"
echo "📡 API Endpoint: https://api.d23.ai"
echo ""

# Navigate to D23Web directory
cd "$(dirname "$0")"

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Creating .env.local with production API endpoint..."
    cat > .env.local << EOF
# D23Web Frontend - QA Environment
NEXT_PUBLIC_API_URL=https://api.d23.ai
EOF
    echo "✅ Created .env.local"
    echo ""
fi

# Display configuration
echo "📋 Configuration:"
echo "   Frontend Port: 5050"
echo "   API Endpoint: $(grep NEXT_PUBLIC_API_URL .env.local | cut -d'=' -f2)"
echo ""

# Start development server
echo "🚀 Starting Next.js development server..."
echo "📊 Admin Dashboard will be available at: http://localhost:5050/admin"
echo "🔐 Login Page: http://localhost:5050/admin/login"
echo ""
echo "Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""

PORT=5050 npm run dev
