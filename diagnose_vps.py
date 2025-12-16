import paramiko
import requests
import sys
import time

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def check_external_access():
    print("\n🔍 [1/4] Checking External Access (HTTP)...")
    url = f"http://{hostname}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ SUCCESS: Website is reachable. Status Code: {response.status_code}")
            if "سوق الإعلانات" in response.text:
                print("✅ CONTENT VERIFIED: Found expected Arabic title.")
            else:
                print("⚠️ WARNING: Content might be different than expected.")
        else:
            print(f"❌ FAILURE: Website returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ FAILURE: Could not connect to {url}. Error: {e}")

def check_internal_health():
    print("\n🔍 [2/4] Checking Internal VPS Health...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        # Check Services
        services = ["nginx", "ads_project"]
        for service in services:
            stdin, stdout, stderr = client.exec_command(f"systemctl is-active {service}")
            status = stdout.read().decode().strip()
            if status == "active":
                print(f"✅ SERVICE: {service} is ACTIVE.")
            else:
                print(f"❌ SERVICE: {service} is {status} (Expected: active).")
                # Get logs if failed
                stdin, stdout, stderr = client.exec_command(f"journalctl -u {service} --no-pager -n 5")
                print(f"   LOGS: {stdout.read().decode().strip()}")

        # Check Port 80
        stdin, stdout, stderr = client.exec_command("netstat -tuln | grep :80")
        if ":80" in stdout.read().decode():
            print("✅ NETWORK: Port 80 is listening.")
        else:
            print("❌ NETWORK: Port 80 is NOT listening.")

        # Check Nginx Config for DNS
        print("\n🔍 [3/4] Checking DNS/Server Configuration...")
        stdin, stdout, stderr = client.exec_command("grep 'server_name' /etc/nginx/sites-enabled/ads_project")
        config_line = stdout.read().decode().strip()
        print(f"ℹ️ CURRENT CONFIG: {config_line}")
        
        if hostname in config_line:
            print("✅ CONFIG MATCH: Nginx is configured for the IP address.")
        else:
            print("⚠️ CONFIG MISMATCH: Nginx might be configured for a domain, but we are accessing via IP.")

        client.close()
    except Exception as e:
        print(f"❌ INTERNAL CHECK FAILED: {e}")

if __name__ == "__main__":
    print(f"--- DIAGNOSTIC REPORT FOR {hostname} ---")
    check_external_access()
    check_internal_health()
    print("\n--- END OF REPORT ---")
