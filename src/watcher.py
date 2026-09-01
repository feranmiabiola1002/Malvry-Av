import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .scanner import Scanner
from .quarantine import Quarantine
from .config import WATCH_FOLDER

class AVEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.scanner = Scanner()
        self.quarantine = Quarantine()
        self.processed = set()
        self.skip_extensions = ['.tmp', '.log', '.cache', '.ini', '.pyc', '.pyo', '.swp']
        self.cooldown = 1  # seconds
    
    def should_process(self, filepath):
        """Check if file should be processed"""
        if filepath in self.processed:
            return False
        if not os.path.isfile(filepath):
            return False
        if os.path.basename(filepath).startswith('.'):
            return False
        if any(filepath.lower().endswith(ext) for ext in self.skip_extensions):
            return False
        # Skip files in quarantine
        if 'quarantine' in filepath.lower():
            return False
        return True
    
    def handle_file(self, filepath):
        """Process a file"""
        if not self.should_process(filepath):
            return
        
        self.processed.add(filepath)
        
        try:
            result = self.scanner.scan_file(filepath)
            if result:
                print(f"[!!!] THREAT DETECTED: {filepath}")
                for det in result:
                    print(f"    -> {det['type']}: {det['name']} ({det['severity']})")
                self.quarantine.isolate(filepath, f"Threat: {result[0]['name']}")
        except Exception as e:
            print(f"[-] Error processing {filepath}: {e}")
        
        # Remove from processed after cooldown
        def remove_from_set():
            time.sleep(self.cooldown)
            self.processed.discard(filepath)
        
        import threading
        threading.Thread(target=remove_from_set, daemon=True).start()
    
    def on_created(self, event):
        if not event.is_directory:
            self.handle_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.handle_file(event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            self.handle_file(event.dest_path)

class FileWatcher:
    def __init__(self, path=None):
        self.path = path or WATCH_FOLDER
        self.observer = Observer()
        self.handler = AVEventHandler()
    
    def start(self):
        """Start watching"""
        print(f"[*] Watching folder: {self.path}")
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()
        print("[+] Real-time protection active")
    
    def stop(self):
        """Stop watching"""
        self.observer.stop()
        self.handler.scanner.close()
        print("[*] Real-time protection stopped")
    
    def join(self):
        self.observer.join()
