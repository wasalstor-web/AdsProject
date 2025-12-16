import paramiko
import sys

class VPSManager:
    def __init__(self):
        self.hostname = "147.93.120.99"
        self.username = "root"
        self.password = "eClAG2giOnJLQ?KG6Ob-"
        self.client = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, username=self.username, password=self.password)
            return True
        except Exception as e:
            print(f"Connection Failed: {e}")
            return False

    def run_command(self, command):
        if not self.client:
            if not self.connect(): return None
        
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode().strip()

    def deploy_full(self):
        if not self.connect(): return

        print("--- STARTING PROFESSIONAL DEPLOYMENT ---")
        
        # 1. Install System Dependencies
        print("[1/6] Installing System Dependencies (Nginx, Python)...")
        self.run_command("apt-get update && apt-get install -y python3-pip python3-venv nginx")

        # 2. Setup Directory & Virtual Environment
        print("[2/6] Setting up Workspace & Virtual Environment...")
        self.run_command("mkdir -p /var/www/AdsProject")
        self.run_command("python3 -m venv /var/www/AdsProject/venv")

        # 3. Upload Files (Using SFTP)
        print("[3/6] Uploading Project Files...")
        sftp = self.client.open_sftp()
        local_path = "C:\\Users\\DealP\\AdsProject"
        remote_path = "/var/www/AdsProject"
        
        files_to_upload = ['app.py', 'requirements.txt', 'ads_project.service', 'ads_project.nginx']
        for f in files_to_upload:
            sftp.put(f"{local_path}\\{f}", f"{remote_path}/{f}")
            
        # Upload folders (simple implementation)
        for folder in ['templates', 'static']:
            self.run_command(f"mkdir -p {remote_path}/{folder}")
            for item in os.listdir(f"{local_path}\\{folder}"):
                sftp.put(f"{local_path}\\{folder}\\{item}", f"{remote_path}/{folder}/{item}")
        sftp.close()

        # 4. Install Python Requirements
        print("[4/6] Installing Python Libraries...")
        self.run_command(f"{remote_path}/venv/bin/pip install -r {remote_path}/requirements.txt")

        # 5. Configure Nginx & Systemd
        print("[5/6] Configuring Server (Nginx & Systemd)...")
        self.run_command(f"cp {remote_path}/ads_project.service /etc/systemd/system/")
        self.run_command(f"cp {remote_path}/ads_project.nginx /etc/nginx/sites-available/ads_project")
        self.run_command("ln -sf /etc/nginx/sites-available/ads_project /etc/nginx/sites-enabled")
        self.run_command("rm -f /etc/nginx/sites-enabled/default") # Remove default site
        self.run_command("nginx -t") # Test config

        # 6. Restart Services
        print("[6/6] Restarting Services...")
        self.run_command("systemctl daemon-reload")
        self.run_command("systemctl start ads_project")
        self.run_command("systemctl enable ads_project")
        self.run_command("systemctl restart ads_project")
        self.run_command("systemctl restart nginx")

        print("\n✅ DEPLOYMENT COMPLETE!")
        print(f"🌍 Site is live at: http://{self.hostname}")
        self.client.close()

if __name__ == "__main__":
    import os
    vps = VPSManager()
    # vps.get_system_status()
    vps.deploy_full()
