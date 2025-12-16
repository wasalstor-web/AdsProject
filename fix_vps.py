import paramiko
import sys
import time

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def run_command(client, command, description):
    print(f"🔧 {description}...")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status != 0:
        print(f"❌ FAILED: {command}")
        print(f"   ERROR: {stderr.read().decode().strip()}")
        return False
    else:
        print(f"✅ DONE.")
        return True

def fix_deployment():
    print("--- STARTING PROFESSIONAL REPAIR ---")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)

        # 1. Clean Slate: Remove broken venv
        run_command(client, "rm -rf /var/www/AdsProject/venv", "Removing broken virtual environment")

        # 2. Recreate Venv
        # Ensure python3-venv is installed first
        run_command(client, "apt-get update && apt-get install -y python3-venv python3-pip", "Ensuring system Python tools are installed")
        run_command(client, "python3 -m venv /var/www/AdsProject/venv", "Creating fresh Virtual Environment")

        # 3. Upgrade Pip inside Venv
        run_command(client, "/var/www/AdsProject/venv/bin/pip install --upgrade pip", "Upgrading Pip")

        # 4. Install Requirements (Verbose to catch errors)
        # We install gunicorn explicitly first to be absolutely sure
        run_command(client, "/var/www/AdsProject/venv/bin/pip install gunicorn==21.2.0", "Installing Gunicorn explicitly")
        # Explicitly install Flask-SQLAlchemy to fix the missing module error
        run_command(client, "/var/www/AdsProject/venv/bin/pip install Flask-SQLAlchemy==3.1.1", "Installing Flask-SQLAlchemy explicitly")
        run_command(client, "/var/www/AdsProject/venv/bin/pip install -r /var/www/AdsProject/requirements.txt", "Installing remaining requirements")

        # 5. Verify Gunicorn Binary
        print("🔧 Verifying Gunicorn installation...")
        stdin, stdout, stderr = client.exec_command("ls -l /var/www/AdsProject/venv/bin/gunicorn")
        if stdout.channel.recv_exit_status() == 0:
            print(f"✅ VERIFIED: {stdout.read().decode().strip()}")
        else:
            print("❌ CRITICAL: Gunicorn binary still missing!")
            client.close()
            return

        # 6. Fix Permissions (Ensure www-data can read/execute)
        run_command(client, "chown -R root:www-data /var/www/AdsProject", "Fixing ownership")
        run_command(client, "chmod -R 755 /var/www/AdsProject", "Fixing permissions")
        # Uploads folder needs write access
        run_command(client, "chmod -R 777 /var/www/AdsProject/static/uploads", "Fixing upload permissions")

        # 7. Restart Service
        run_command(client, "systemctl restart ads_project", "Restarting Application Service")
        
        # 8. Check Status
        time.sleep(2) # Wait for startup
        stdin, stdout, stderr = client.exec_command("systemctl is-active ads_project")
        status = stdout.read().decode().strip()
        if status == "active":
            print("\n✅ REPAIR SUCCESSFUL: Service is ACTIVE.")
        else:
            print(f"\n❌ REPAIR FAILED: Service status is {status}")
            stdin, stdout, stderr = client.exec_command("journalctl -u ads_project --no-pager -n 10")
            print(stdout.read().decode())

        client.close()

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    fix_deployment()
