# python_dns_debug.py - Debug Python DNS resolution
import socket
import subprocess
import sys

def test_python_dns():
    """Test Python's DNS resolution capabilities"""
    hostname = "db.khyqmssuchivbrufloxs.supabase.co"
    
    print("=== Python DNS Resolution Tests ===")
    
    # Test 1: Basic gethostbyname
    print("1️⃣ Testing socket.gethostbyname()...")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ SUCCESS: {hostname} → {ip}")
        return ip
    except socket.gaierror as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: getaddrinfo with different parameters
    print("\n2️⃣ Testing socket.getaddrinfo() variations...")
    
    test_configs = [
        (socket.AF_UNSPEC, "Any family"),
        (socket.AF_INET, "IPv4 only"),
        (socket.AF_INET6, "IPv6 only"),
    ]
    
    for family, desc in test_configs:
        try:
            result = socket.getaddrinfo(hostname, 5432, family)
            if result:
                addr = result[0][4][0] if result[0][4] else "Unknown"
                print(f"✅ {desc}: {addr}")
                if family == socket.AF_INET:
                    return addr
        except socket.gaierror as e:
            print(f"❌ {desc}: {e}")
    
    # Test 3: Try with known working hostname
    print("\n3️⃣ Testing with google.com (should work)...")
    try:
        ip = socket.gethostbyname("google.com")
        print(f"✅ Google resolves to: {ip}")
    except socket.gaierror as e:
        print(f"❌ Even Google failed: {e}")
    
    return None

def test_system_dns():
    """Test system DNS resolution"""
    print("\n=== System DNS Test ===")
    hostname = "db.khyqmssuchivbrufloxs.supabase.co"
    
    try:
        # Run nslookup from Python
        result = subprocess.run(
            ["nslookup", hostname, "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ System nslookup works from Python")
            print("Output:", result.stdout[-200:])  # Last 200 chars
        else:
            print("❌ System nslookup failed from Python")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"❌ Could not run system nslookup: {e}")

def test_python_environment():
    """Test Python environment specifics"""
    print("\n=== Python Environment Info ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Has IPv6: {socket.has_ipv6}")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'base_prefix'):
        if sys.base_prefix != sys.prefix:
            print("✅ Running in virtual environment")
        else:
            print("❌ Not in virtual environment")
    
    # Test default socket timeout
    print(f"Default socket timeout: {socket.getdefaulttimeout()}")

def manual_ip_resolution():
    """Try to manually resolve using subprocess"""
    print("\n=== Manual Resolution Attempt ===")
    hostname = "db.khyqmssuchivbrufloxs.supabase.co"
    
    try:
        # Use Windows nslookup to get IP
        result = subprocess.run(
            ["nslookup", hostname],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Address:' in line and '::' not in line and '.' in line:
                    # Found IPv4 address
                    ip = line.split()[-1]
                    if ip.count('.') == 3:  # Valid IPv4 format
                        print(f"🔍 Found IPv4 from nslookup: {ip}")
                        return ip
        
        print("❌ Could not extract IP from nslookup")
        return None
        
    except Exception as e:
        print(f"❌ Manual resolution failed: {e}")
        return None

def main():
    print("🔍 Debugging Python DNS resolution issue...\n")
    
    # Run all tests
    python_ip = test_python_dns()
    test_system_dns()
    test_python_environment()
    manual_ip = manual_ip_resolution()
    
    print("\n=== Summary & Solutions ===")
    
    if python_ip:
        print(f"✅ Python resolved IP: {python_ip}")
        print("💡 Try using this IP in your .env file")
    elif manual_ip:
        print(f"✅ Manual resolution found IP: {manual_ip}")
        print("💡 Use this IP address in your .env file:")
        print(f"   DB_HOST={manual_ip}")
    else:
        print("❌ All resolution methods failed")
        print("💡 Possible solutions:")
        print("1. Try running outside virtual environment")
        print("2. Reinstall Python network libraries:")
        print("   pip install --upgrade --force-reinstall psycopg2-binary")
        print("3. Try different Python version")
        print("4. Check Windows network stack issues")

if __name__ == "__main__":
    main()