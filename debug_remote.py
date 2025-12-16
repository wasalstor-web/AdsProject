import paramiko
import sys

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def debug_app():
    print("--- DEBUGGING FLASK APP ON SERVER ---")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)

        # Try to run the app manually to see the traceback
        print("Running: python app.py (Manual Test)...")
        cmd = "cd /var/www/AdsProject && ./venv/bin/python app.py"
        
        # We use invoke_shell or just exec_command. exec_command is better for capturing stderr.
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Wait a bit for output
        import time
        time.sleep(2)
        
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        print(f"\n[STDOUT]\n{out}")
        print(f"\n[STDERR]\n{err}")
        
        client.close()

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    debug_app()
