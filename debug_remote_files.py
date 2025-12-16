import paramiko

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def debug_remote():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- REMOTE FILE CHECK ---")
        
        # Check templates directory
        print("\n[1] Listing templates directory:")
        stdin, stdout, stderr = client.exec_command("ls -la /var/www/AdsProject/templates")
        print(stdout.read().decode())
        
        # Check index.html content (first 10 lines)
        print("\n[2] Content of index.html (head):")
        stdin, stdout, stderr = client.exec_command("head -n 20 /var/www/AdsProject/templates/index.html")
        print(stdout.read().decode())

        # Check app.py content (first 20 lines)
        print("\n[3] Content of app.py (head):")
        stdin, stdout, stderr = client.exec_command("head -n 20 /var/www/AdsProject/app.py")
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_remote()
