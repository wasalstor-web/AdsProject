import paramiko

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def deep_diagnose():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- DEEP DIAGNOSTIC ---")
        
        # 1. Check Nginx Config
        print("\n[1] Nginx Configuration:")
        stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/ads_project")
        print(stdout.read().decode())
        
        # 2. Check Running Processes
        print("\n[2] Running Gunicorn Processes:")
        stdin, stdout, stderr = client.exec_command("ps aux | grep gunicorn")
        print(stdout.read().decode())
        
        # 3. Check Socket File
        print("\n[3] Socket File Status:")
        stdin, stdout, stderr = client.exec_command("ls -la /var/www/AdsProject/ads_project.sock")
        print(stdout.read().decode())

        # 4. Check what is listening on port 80
        print("\n[4] Port 80 Listener:")
        stdin, stdout, stderr = client.exec_command("netstat -tulpn | grep :80")
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deep_diagnose()
