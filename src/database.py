import sqlite3
import os
from .config import DB_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hash TEXT UNIQUE,
                yara_rule TEXT,
                severity TEXT DEFAULT 'medium',
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                signature_id INTEGER,
                detection_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signature_id) REFERENCES signatures(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def init_cloud_db(self):
        """Initialize database for cloud deployment"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS signatures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                hash TEXT UNIQUE,
                yara_rule TEXT,
                severity TEXT DEFAULT 'medium',
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                signature_id INTEGER,
                detection_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signature_id) REFERENCES signatures(id)
            )
        ''')
        self.conn.commit()
    
    def add_signature(self, name, file_hash=None, yara_rule=None, severity='medium'):
        """Add a new signature"""
        try:
            self.cursor.execute(
                "INSERT INTO signatures (name, hash, yara_rule, severity) VALUES (?, ?, ?, ?)",
                (name, file_hash, yara_rule, severity)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_signature_by_hash(self, file_hash):
        """Get signature by hash"""
        self.cursor.execute("SELECT id, name, severity FROM signatures WHERE hash=?", (file_hash,))
        return self.cursor.fetchone()
    
    def get_all_yara_rules(self):
        """Get all YARA rules"""
        self.cursor.execute("SELECT name, yara_rule FROM signatures WHERE yara_rule IS NOT NULL")
        return self.cursor.fetchall()
    
    def log_detection(self, file_path, signature_id, detection_type):
        """Log a detection"""
        self.cursor.execute(
            "INSERT INTO detections (file_path, signature_id, detection_type) VALUES (?, ?, ?)",
            (file_path, signature_id, detection_type)
        )
        self.conn.commit()
    
    def get_stats(self):
        """Get detection statistics"""
        self.cursor.execute("SELECT COUNT(*) FROM detections")
        total_detections = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM signatures")
        total_signatures = self.cursor.fetchone()[0]
        
        return {
            'total_detections': total_detections,
            'total_signatures': total_signatures
        }
    
    def close(self):
        self.conn.close()

def init_default_signatures():
    """Initialize database with default signatures"""
    db = Database()
    
    # Hash signatures
    signatures = [
        ('EICAR Test', '44d88612fea8a8f36de82e1278abb02f', None, 'high'),
        ('Ransomware_WannaCry', '4a6f5c2e7b9d4f1a8c3e5f7b9d1e2f3a', None, 'critical'),
        ('Trojan_Generic', '9f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c', None, 'medium'),
        ('Malware_Test', '5d41402abc4b2a76b9719d911017c592', None, 'low'),
        ('Test_Virus', '098f6bcd4621d373cade4e832627b4f6', None, 'medium'),
    ]
    
    for name, hash_val, rule, severity in signatures:
        db.add_signature(name, hash_val, rule, severity)
    
    # YARA rule
    yara_rule = """
rule Test_Rule {
    strings:
        $a = "MALVRYX_AV_TEST"
        $b = "SUSPICIOUS"
        $c = "VIRUS"
        $d = "MALWARE"
    condition:
        any of them
}
"""
    db.add_signature('YARA_Test_Rule', None, yara_rule, 'high')
    
    db.close()
    print("[+] Default signatures loaded")
