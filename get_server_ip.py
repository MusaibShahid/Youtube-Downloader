#!/usr/bin/env python3
"""
Get server IP address for network access
"""

import socket
import platform

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except:
        return "127.0.0.1"

def main():
    print("🌐 Server IP Address Information")
    print("=" * 40)
    
    local_ip = get_local_ip()
    print(f"📱 Local IP: {local_ip}")
    print(f"🔌 Port: 5000")
    print(f"🌐 Server URL: http://{local_ip}:5000")
    print(f"🏠 Local URL: http://localhost:5000")
    
    print("\n📋 Access URLs:")
    print(f"   • From this device: http://localhost:5000")
    print(f"   • From other devices: http://{local_ip}:5000")
    
    print("\n💡 To start server mode:")
    print("   Windows: start_server.bat")
    print("   Linux/macOS: ./start_server.sh")
    print("   Or: set YT_SERVER_MODE=true && python app.py")

if __name__ == "__main__":
    main()
