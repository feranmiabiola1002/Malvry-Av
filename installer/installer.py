import os
import sys
import subprocess
import shutil
import ctypes
import winreg
import platform

class MalvryxInstaller:
    def __init__(self):
        self.install_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'MalvryxAV')
        self.appdata = os.environ.get('APPDATA')
        self.startup_folder = os.path.join(self.appdata, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        self.desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        self.python_exe = sys.executable
        
    def check_admin(self):
        if not self.is_admin:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    
    def copy_files(self):
        print("[*] Installing files...")
        os.makedirs(self.install_path, exist_ok=True)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.join(script_dir, '..', 'src')
        files_to_copy = ['main.py', 'scanner.py', 'behavior.py', 'quarantine.py', 'watcher.py', 'database.py', 'config.py', 'web_server.py', '__init__.py']
        for f in files_to_copy:
            src = os.path.join(src_dir, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(self.install_path, f))
                print(f"[+] Copied: {f}")
        for d in ['quarantine', 'logs', 'watch_folder']:
            os.makedirs(os.path.join(self.install_path, d), exist_ok=True)
    
    def install_dependencies(self):
        print("[*] Installing dependencies...")
        try:
            subprocess.run([self.python_exe, '-m', 'pip', 'install', 'yara-python', 'psutil', 'watchdog', 'flask'], capture_output=True, cwd=self.install_path, timeout=300)
            print("[+] Dependencies installed")
        except:
            print("[-] Dependency install error")
    
    def create_startup_files(self):
        print("[*] Creating startup files...")
        batch_path = os.path.join(self.install_path, 'start_av.bat')
        with open(batch_path, 'w') as f:
            f.write(f'@echo off\n"{self.python_exe}" "{os.path.join(self.install_path, "main.py")}" watch\n')
        # Desktop shortcut
        vbs = os.path.join(self.desktop, 'shortcut.vbs')
        with open(vbs, 'w') as f:
            f.write(f'''
Set oWS = WScript.CreateObject("WScript.Shell")
Set oLink = oWS.CreateShortcut("{self.desktop}\\MalvryxAV.lnk")
oLink.TargetPath = "{self.python_exe}"
oLink.Arguments = '"{os.path.join(self.install_path, "main.py")}" watch'
oLink.WorkingDirectory = "{self.install_path}"
oLink.Save()
''')
        subprocess.run(['cscript', vbs], capture_output=True)
        os.remove(vbs)
        print("[+] Shortcuts created")
    
    def add_registry(self):
        print("[*] Adding to registry...")
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(handle, "MalvryxAV", 0, winreg.REG_SZ, f'"{self.python_exe}" "{os.path.join(self.install_path, "main.py")}" watch')
            winreg.CloseKey(handle)
            print("[+] Registry entry added")
        except:
            print("[-] Registry error")
    
    def create_uninstaller(self):
        print("[*] Creating uninstaller...")
        with open(os.path.join(self.install_path, 'uninstall.bat'), 'w') as f:
            f.write(f'''
@echo off
echo Uninstalling Malvryx AV...
taskkill /f /im python.exe 2>nul
rmdir /s /q "{self.install_path}" 2>nul
reg delete "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v MalvryxAV /f 2>nul
del "{self.desktop}\\MalvryxAV.lnk" 2>nul
echo Uninstall complete.
pause
''')
    
    def initialize_database(self):
        print("[*] Initializing database...")
        try:
            subprocess.run([self.python_exe, os.path.join(self.install_path, 'main.py'), 'init'], cwd=self.install_path, capture_output=True, timeout=60)
            print("[+] Database initialized")
        except:
            print("[-] Database init error")
    
    def start_protection(self):
        print("[*] Starting Malvryx AV...")
        try:
            subprocess.Popen([self.python_exe, os.path.join(self.install_path, 'main.py'), 'watch'], creationflags=subprocess.CREATE_NO_WINDOW, cwd=self.install_path)
            print("[+] Protection started")
        except:
            print("[-] Start error")
    
    def install(self):
        print("""
╔═══════════════════════════════════════════╗
║   MALVRYX AV - One-Click Installer       ║
║   Version 1.0.0                          ║
║   Next-Generation Protection             ║
╚═══════════════════════════════════════════╝
        """)
        self.check_admin()
        print("[+] Admin privileges confirmed")
        self.copy_files()
        self.install_dependencies()
        self.create_startup_files()
        self.add_registry()
        self.create_uninstaller()
        self.initialize_database()
        self.start_protection()
        print("""
        ✅ INSTALLATION COMPLETE!
        Malvryx AV is now protecting your system.
        Installation folder: """ + self.install_path + """
        """)
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    installer = MalvryxInstaller()
    installer.install()
