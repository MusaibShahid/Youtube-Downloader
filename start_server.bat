@echo off
title YouTube Downloader - SERVER MODE
color 0B

echo.
echo  ================================================
echo  🌐 YouTube Downloader - SERVER MODE
echo  ================================================
echo.
echo  📱 Accessible from other devices on network
echo  💻 Using server resources
echo  🔓 Network access enabled
echo.

set YT_SERVER_MODE=true
python app.py

echo.
echo  👋 YouTube Downloader server stopped
pause
