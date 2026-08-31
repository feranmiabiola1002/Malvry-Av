#!/usr/bin/env python3
import sys
import time
import argparse
import threading
import os
import subprocess
import json

# Import from same folder
from .scanner import Scanner
from .behavior import BehaviorMonitor
from .quarantine import Quarantine
from .watcher import FileWatcher
from .database import init_default_signatures
from .config import WATCH_FOLDER, VERSION, IS_CLOUD

class MalvryxAV:
    def __init__(self):
        self.scanner = Scanner()
        self.behavior = BehaviorMonitor()
        self.quarantine = Quarantine()
        self.watcher = None
        self.running = True
    
    def scan(self, path, full=False):
        if full:
            path = 'C:\\' if sys.platform == 'win32' else '/'
        return self.scanner.scan_directory(path)
    
    def monitor(self):
        return self.behavior.scan_running_processes()
    
    def watch(self):
        self.watcher = FileWatcher()
        self.watcher.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def list_quarantine(self):
        return self.quarantine.list_quarantined()
    
    def restore(self, index):
        return self.quarantine.restore(index)
    
    def delete_quarantine(self, index):
        return self.quarantine.delete_quarantine(index)
    
    def check_updates(self):
        try:
            import requests
            response = requests.get(
                'https://raw.githubusercontent.com/malvryx/malvryx-av/main/version.json',
                timeout=5
            )
            latest = response.json()
            if latest.get('version', '0') > VERSION:
                print(f"[!] New version {latest['version']} available!")
                print("[*] Downloading update...")
                installer = requests.get(latest['installer_url'])
                with open('MalvryxAV_Update.exe', 'wb') as f:
                    f.write(installer.content)
                print("[+] Update downloaded. Run MalvryxAV_Update.exe to install.")
                return True
            else:
                print("[+] You have the latest version")
                return False
        except Exception as e:
            print(f"[-] Update check failed: {e}")
            return False
    
    def start_web(self, port=5000):
        from .web_server import app
        app.run(host='0.0.0.0', port=port, debug=False)
    
    def start_cloud(self):
        from .web_server import app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    
    def stop(self):
        self.running = False
        if self.watcher:
            self.watcher.stop()
        self.scanner.close()
        print("[+] Shutdown complete")

def main():
    parser = argparse.ArgumentParser(description='Malvryx AV Engine')
    parser.add_argument('command', nargs='?', default='help',
                       choices=['init', 'scan', 'monitor', 'watch', 'web', 'cloud',
                               'quarantine', 'restore', 'delete', 'update', 'help'])
    parser.add_argument('--path', default='./watch_folder', help='Path to scan')
    parser.add_argument('--index', type=int, help='Quarantine item index')
    parser.add_argument('--full', action='store_true', help='Full system scan')
    parser.add_argument('--port', type=int, default=5000, help='Web server port')
    
    args = parser.parse_args()
    av = MalvryxAV()
    
    if args.command == 'init':
        print("[*] Initializing database...")
        init_default_signatures()
        print("[+] Database initialized")
    elif args.command == 'scan':
        results = av.scan(args.path, args.full)
        if results:
            print(f"\n[!] {len(results)} threats found")
            for file, detections in results:
                print(f"  {file}")
                for det in detections:
                    print(f"    -> {det['type']}: {det['name']} ({det['severity']})")
        else:
            print("[+] No threats found")
    elif args.command == 'monitor':
        print("[*] Monitoring running processes...")
        alerts = av.monitor()
        if alerts:
            print(f"[!] {len(alerts)} suspicious processes found")
            for pid, alert in alerts:
                print(f"  PID {pid}: {alert}")
        else:
            print("[+] No suspicious processes detected")
    elif args.command == 'watch':
        print("[*] Starting real-time protection...")
        av.watch()
    elif args.command == 'web':
        av.start_web(args.port)
    elif args.command == 'cloud':
        av.start_cloud()
    elif args.command == 'quarantine':
        av.list_quarantine()
    elif args.command == 'restore':
        if args.index is None:
            print("[-] Please specify --index")
        else:
            av.restore(args.index)
    elif args.command == 'delete':
        if args.index is None:
            print("[-] Please specify --index")
        else:
            av.delete_quarantine(args.index)
    elif args.command == 'update':
        av.check_updates()
    else:
        print(f"""
╔═══════════════════════════════════════════╗
║   MALVRYX AV v{VERSION}                        ║
║   Next-Generation Antivirus Engine       ║
╚═══════════════════════════════════════════╝

Commands:
  init              - Initialize database
  scan --path /path - Scan a directory
  scan --full       - Full system scan
  monitor           - Monitor running processes
  watch             - Start real-time protection
  web --port 5000   - Start web dashboard
  cloud             - Start in cloud mode (Render/Vercel)
  quarantine        - List quarantined files
  restore --index N - Restore from quarantine
  delete --index N  - Delete from quarantine permanently
  update            - Check for updates

Examples:
  python -m src.main init
  python -m src.main scan --path C:/Downloads
  python -m src.main watch
  python -m src.main web --port 5000
        """)
    av.stop()

if __name__ == "__main__":
    main()
