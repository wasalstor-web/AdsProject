import paramiko

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def init_db_remote():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- INITIALIZING DATABASE ---")
        
        # Run python command to create tables
        cmd = "/var/www/AdsProject/venv/bin/python3 -c 'from app import app, db; app.app_context().push(); db.create_all(); print(\"Tables Created\")'"
        
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(f"cd /var/www/AdsProject && {cmd}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init_db_remote()
