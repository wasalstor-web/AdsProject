import paramiko
import time

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def force_restart():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- FORCING SERVICE RESTART ---")
        
        # 1. Stop Service
        print("[1] Stopping ads_project service...")
        client.exec_command("systemctl stop ads_project")
        time.sleep(2)
        
        # 2. Kill any lingering Gunicorn processes
        print("[2] Killing lingering Gunicorn processes...")
        client.exec_command("pkill gunicorn")
        time.sleep(2)
        
        # 3. Remove old database to prevent schema conflicts (since we changed models)
        print("[3] Resetting Database (removing old SQLite files)...")
        client.exec_command("rm -f /var/www/AdsProject/*.db")
        client.exec_command("rm -f /var/www/AdsProject/instance/*.db")
        
        # 4. Start Service
        print("[4] Starting ads_project service...")
        client.exec_command("systemctl start ads_project")
        time.sleep(3)
        
        # 5. Check Status
        print("[5] Checking Service Status:")
        stdin, stdout, stderr = client.exec_command("systemctl status ads_project")
        print(stdout.read().decode())
        
        # 6. Check Logs
        print("\n[6] Recent Logs:")
        stdin, stdout, stderr = client.exec_command("journalctl -u ads_project -n 20 --no-pager")
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_restart()
