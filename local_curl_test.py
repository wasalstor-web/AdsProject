import paramiko

hostname = "147.93.120.99"
username = "root"
password = "eClAG2giOnJLQ?KG6Ob-"

def local_curl_test():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)
        
        print("--- LOCAL CURL TEST ---")
        
        # 1. Curl Localhost
        print("\n[1] Curl http://localhost/")
        stdin, stdout, stderr = client.exec_command("curl -s http://localhost/ | grep '<title>'")
        print(stdout.read().decode())
        
        # 2. Curl Upload Page
        print("\n[2] Curl http://localhost/upload")
        stdin, stdout, stderr = client.exec_command("curl -s http://localhost/upload | grep 'TikTok'")
        print(stdout.read().decode())

        # 3. Done
        print("\n[3] Done.")
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    local_curl_test()
