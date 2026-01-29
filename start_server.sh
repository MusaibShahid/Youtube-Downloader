#!/bin/bash
# YouTube Downloader - SERVER MODE

echo "================================================"
echo "🌐 YouTube Downloader - SERVER MODE"
echo "================================================"
echo ""
echo "📱 Accessible from other devices on network"
echo "💻 Using server resources"
echo "🔓 Network access enabled"
echo ""

export YT_SERVER_MODE=true
python3 app.py

echo ""
echo "👋 YouTube Downloader server stopped"
