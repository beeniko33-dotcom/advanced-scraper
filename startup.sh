#!/data/data/com.termux/files/usr/bin/bash
cd ~/advanced-scraper
echo "🚀 Starting API Server..."
python api_server.py &
sleep 5
echo "🌐 Starting Cloudflare Tunnel..."
cloudflared tunnel --url http://127.0.0.1:8000 &
echo "📡 Starting Wardrive Bot..."
python wardrive.py &
echo "✅ All systems online. Use Ctrl+C to stop all."
wait
