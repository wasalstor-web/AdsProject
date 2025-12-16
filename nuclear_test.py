import paramiko
import time

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def nuclear_test():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- NUCLEAR TEST ---")
        
        # 1. Rename templates directory
        print("[1] Renaming templates directory to templates_bak...")
        client.exec_command("mv /var/www/AdsProject/templates /var/www/AdsProject/templates_bak")
        
        # 2. Restart Gunicorn
        print("[2] Restarting Gunicorn...")
        client.exec_command("systemctl restart ads_project")
        time.sleep(3)
        
        print("Now check the website. It should be broken (500 Error).")
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    nuclear_test()
