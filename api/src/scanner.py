import os
import hashlib
import yara
import time
from config import MAX_FILE_SIZE, SCAN_TIMEOUT
from database import Database

class Scanner:
    def __init__(self):
        self.db = Database()
        self.yara_rules = None
        self.compile_yara_rules()
    
    def compile_yara_rules(self):
        rules = self.db.get_all_yara_rules()
        if rules:
            try:
                rule_source = '\n'.join([r[1] for r in rules if r[1]])
                self.yara_rules = yara.compile(source=rule_source)
            except Exception as e:
                print(f"[-] YARA compile error: {e}")
                self.yara_rules = None
    
    def get_file_hash(self, filepath):
        try:
            hasher = hashlib.md5()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    def scan_file(self, filepath):
        if not os.path.isfile(filepath):
            return None
        
        try:
            file_size = os.path.getsize(filepath)
            if file_size > MAX_FILE_SIZE:
                return [{'type': 'skipped', 'name': 'File too large', 'severity': 'info'}]
        except:
            return None
        
        detections = []
        
        # 1. Hash-based detection
        file_hash = self.get_file_hash(filepath)
        if file_hash:
            sig = self.db.get_signature_by_hash(file_hash)
            if sig:
                sig_id, name, severity = sig
                detections.append({
                    'type': 'hash_match',
                    'name': name,
                    'severity': severity,
                    'id': sig_id
                })
                self.db.log_detection(filepath, sig_id, 'hash_match')
        
        # 2. YARA-based detection
        if self.yara_rules and not detections:
            try:
                matches = self.yara_rules.match(filepath, timeout=SCAN_TIMEOUT)
                for match in matches:
                    sig = self.db.cursor.execute(
                        "SELECT id, severity FROM signatures WHERE yara_rule LIKE ?",
                        (f'%{match.rule}%',)
                    ).fetchone()
                    if sig:
                        sig_id, severity = sig
                        detections.append({
                            'type': 'yara_match',
                            'name': match.rule,
                            'severity': severity,
                            'id': sig_id
                        })
                        self.db.log_detection(filepath, sig_id, 'yara_match')
            except Exception as e:
                pass
        
        return detections if detections else None
    
    def scan_directory(self, path):
        """Scan entire directory recursively"""
        if not os.path.exists(path):
            print(f"[-] Path does not exist: {path}")
            return []
        
        infected = []
        total = 0
        print(f"[*] Scanning: {path}")
        
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                total += 1
                if total % 100 == 0:
                    print(f"[*] Scanned {total} files...")
                
                result = self.scan_file(full_path)
                if result:
                    infected.append((full_path, result))
                    print(f"[!] INFECTED: {full_path}")
                    for det in result:
                        print(f"    -> {det['type']}: {det['name']} ({det['severity']})")
        
        print(f"[+] Complete. {len(infected)} threats found out of {total} files.")
        return infected
    
    def close(self):
        self.db.close()
