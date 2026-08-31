import psutil
from config import CPU_THRESHOLD, MEMORY_THRESHOLD

class BehaviorMonitor:
    def __init__(self):
        self.suspicious = []
        self.known_good = [
            'svchost.exe', 'explorer.exe', 'winlogon.exe', 
            'services.exe', 'system', 'python.exe', 'conhost.exe',
            'dwm.exe', 'taskhost.exe', 'csrss.exe', 'lsass.exe'
        ]
    
    def analyze_process(self, pid):
        try:
            proc = psutil.Process(pid)
            alerts = []
            
            # CPU usage
            cpu = proc.cpu_percent(interval=0.1)
            if cpu > CPU_THRESHOLD:
                alerts.append(f"High CPU: {cpu}%")
            
            # Memory usage
            mem = proc.memory_percent()
            if mem > MEMORY_THRESHOLD:
                alerts.append(f"High Memory: {mem}%")
            
            # Network connections
            try:
                for conn in proc.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        alerts.append(f"Network connection to {conn.raddr.ip}:{conn.raddr.port}")
            except:
                pass
            
            # Suspicious process name check
            if proc.name().lower() not in [g.lower() for g in self.known_good]:
                if alerts:
                    alerts.append(f"Unusual process: {proc.name()}")
            
            if alerts:
                self.suspicious.append({
                    'pid': pid,
                    'name': proc.name(),
                    'alerts': alerts,
                    'cpu': cpu,
                    'memory': mem
                })
                return alerts
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return []
    
    def scan_running_processes(self):
        """Scan all running processes for suspicious behavior"""
        alerts = []
        for proc in psutil.process_iter(['pid']):
            try:
                result = self.analyze_process(proc.info['pid'])
                if result:
                    alerts.append((proc.info['pid'], result))
                    print(f"[!] PID {proc.info['pid']}: {result}")
            except:
                pass
        return alerts
    
    def get_suspicious(self):
        """Return and clear suspicious processes list"""
        suspicious = self.suspicious.copy()
        self.suspicious = []
        return suspicious
