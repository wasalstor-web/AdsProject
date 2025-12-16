import paramiko

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def create_admin_remote():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- CREATING ADMIN USER ---")
        
        # Run flask command to create admin
        cmd = "export FLASK_APP=app.py && /var/www/AdsProject/venv/bin/flask create-admin"
        
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(f"cd /var/www/AdsProject && {cmd}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin_remote()
