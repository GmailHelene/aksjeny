import socket
import subprocess
import sys

def check_port_5000():
    """Check if port 5000 is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("✅ Port 5000 is in use (server might be running)")
        return True
    else:
        print("❌ Port 5000 is not in use (no server running)")
        return False

def check_processes():
    """Check what's running on port 5000"""
    try:
        result = subprocess.run(['lsof', '-i', ':5000'], 
                              capture_output=True, text=True)
        if result.stdout:
            print("🔍 Processes on port 5000:")
            print(result.stdout)
        else:
            print("❌ No processes found on port 5000")
    except:
        print("⚠️ Could not check processes (lsof not available)")

def kill_existing_servers():
    """Kill any existing servers on port 5000"""
    try:
        subprocess.run(['pkill', '-f', 'python.*5000'], 
                      capture_output=True)
        print("🔄 Killed existing Python servers")
    except:
        print("⚠️ Could not kill existing servers")

if __name__ == "__main__":
    print("🔍 Debugging connection issue...")
    print("=" * 40)
    
    check_port_5000()
    check_processes()
    
    choice = input("\nKill existing servers and start fresh? (y/n): ")
    if choice.lower() == 'y':
        kill_existing_servers()
        print("🚀 Now run: python3 test_server.py")
