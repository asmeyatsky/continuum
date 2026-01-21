#!/bin/bash
echo "🚀 ACTIVATING GARDEN WALL - Real Data Pipeline"
echo "================================================="

# Install required packages
pip install aiohttp beautifulsoup4 lxml feedparser

# Update .env with real search
echo "📝 Updating configuration..."
cat >> .env << EOF

# ACTIVATE REAL SEARCH NOW
FEATURE_REAL_WEB_SEARCH=true
FEATURE_COMPREHENSIVE_SEARCH=true

# Add at least ONE API key below:
BRAVE_SEARCH_API_KEY=your_brave_key_here
# OR
TAVILY_API_KEY=your_tavily_key_here  
# OR
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_google_cse_id

# Extended sources (optional but powerful)
GITHUB_TOKEN=ghp_your_github_token
YOUTUBE_API_KEY=AIzaSy_youtube_key
EOF

echo "✅ Configuration updated!"
echo ""
echo "🎯 READY TO LAUNCH:"
echo "   python -m api.app"
echo ""
echo "🌐 Then test with:"
echo "   curl -X POST http://localhost:8000/api/comprehensive-search"
echo "   -H 'Content-Type: application/json'" 
echo "   -d '{\"query\": \"artificial intelligence\", \"limit\": 20}'"
echo ""
echo "🎉 GARDEN WALL REACHED! No more mock data!"