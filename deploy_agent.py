import paramiko
import os
import sys

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def run_command(client, command):
    print(f"EXEC: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    return exit_status

try:
    print(f"Connecting to {hostname} using PASSWORD...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    print("SUCCESS: Connected as Agent.")

    # 1. Prepare Directory
    run_command(client, "mkdir -p /var/www/AdsProject")
    
    # 2. Install System Dependencies (Python/Pip)
    # Check if python3 is installed
    run_command(client, "python3 --version")
    # Install pip if missing (assuming Debian/Ubuntu or CentOS)
    # We'll try a generic update/install command safely
    # run_command(client, "apt-get update && apt-get install -y python3-pip") 

    client.close()
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
