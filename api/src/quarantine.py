import os
import zipfile
import datetime
import json
from config import QUARANTINE_DIR, QUARANTINE_PASSWORD

class Quarantine:
    def __init__(self):
        self.quarantine_dir = QUARANTINE_DIR
        self.manifest_file = os.path.join(QUARANTINE_DIR, 'manifest.json')
        self.manifest = self.load_manifest()
    
    def load_manifest(self):
        if os.path.exists(self.manifest_file):
            try:
                with open(self.manifest_file, 'r') as f:
                    return json.load(f)
            except:
                return {'items': []}
        return {'items': []}
    
    def save_manifest(self):
        try:
            with open(self.manifest_file, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            print(f"[-] Failed to save manifest: {e}")
    
    def isolate(self, filepath, reason):
        """Isolate a file to quarantine"""
        if not os.path.exists(filepath):
            print(f"[-] File not found: {filepath}")
            return None
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = os.path.basename(filepath)
        zip_name = f"{original_name}_{timestamp}.zip"
        zip_path = os.path.join(self.quarantine_dir, zip_name)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.setpassword(QUARANTINE_PASSWORD)
                zf.write(filepath, original_name)
            
            self.manifest['items'].append({
                'original_path': filepath,
                'quarantine_path': zip_path,
                'timestamp': timestamp,
                'reason': reason,
                'size': os.path.getsize(filepath)
            })
            self.save_manifest()
            
            # Remove original file
            try:
                os.remove(filepath)
                print(f"[✓] Quarantined: {filepath}")
            except Exception as e:
                print(f"[-] Could not delete original: {e}")
            
            return zip_path
            
        except Exception as e:
            print(f"[-] Quarantine failed for {filepath}: {e}")
            return None
    
    def list_quarantined(self):
        """List all quarantined items"""
        if not self.manifest['items']:
            print("[*] No files in quarantine")
            return []
        
        print("\n=== Quarantined Files ===")
        for i, item in enumerate(self.manifest['items']):
            print(f"{i}. {os.path.basename(item['original_path'])}")
            print(f"   Reason: {item['reason']}")
            print(f"   Date: {item['timestamp']}")
            print(f"   Size: {item.get('size', 0)} bytes")
            print()
        
        return self.manifest['items']
    
    def restore(self, index):
        """Restore a file from quarantine"""
        if not 0 <= index < len(self.manifest['items']):
            print(f"[-] Invalid index: {index}")
            return False
        
        item = self.manifest['items'][index]
        zip_path = item['quarantine_path']
        original_path = item['original_path']
        
        if not os.path.exists(zip_path):
            print(f"[-] Quarantine file not found: {zip_path}")
            return False
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(os.path.dirname(original_path), pwd=QUARANTINE_PASSWORD)
            
            self.manifest['items'].pop(index)
            self.save_manifest()
            
            print(f"[✓] Restored: {original_path}")
            return True
            
        except Exception as e:
            print(f"[-] Restore failed: {e}")
            return False
    
    def delete_quarantine(self, index):
        """Permanently delete a quarantined item"""
        if not 0 <= index < len(self.manifest['items']):
            print(f"[-] Invalid index: {index}")
            return False
        
        item = self.manifest['items'][index]
        zip_path = item['quarantine_path']
        
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            self.manifest['items'].pop(index)
            self.save_manifest()
            print(f"[✓] Deleted quarantined file permanently")
            return True
        except Exception as e:
            print(f"[-] Delete failed: {e}")
            return False
