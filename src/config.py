import os

# Version
VERSION = "1.0.0"

# ========== CLOUD DEPLOYMENT DETECTION ==========
IS_RENDER = os.environ.get('RENDER') == 'true'
IS_VERCEL = os.environ.get('VERCEL') == '1'
IS_CLOUD = IS_RENDER or IS_VERCEL

# ========== PATHS ==========
if IS_RENDER or IS_VERCEL:
    # Cloud platforms use /tmp for ephemeral storage
    BASE_DIR = '/tmp'
    DB_PATH = '/tmp/signatures.db'
    QUARANTINE_DIR = '/tmp/quarantine'
    LOGS_DIR = '/tmp/logs'
    WATCH_FOLDER = '/tmp/watch_folder'
else:
    # Local development
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'signatures.db')
    QUARANTINE_DIR = os.path.join(BASE_DIR, 'quarantine')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    WATCH_FOLDER = os.path.join(BASE_DIR, 'watch_folder')

# Create directories (skip on Vercel - read-only filesystem)
if not IS_VERCEL:
    for dir_path in [QUARANTINE_DIR, LOGS_DIR, WATCH_FOLDER]:
        try:
            os.makedirs(dir_path, exist_ok=True)
        except:
            pass

# ========== SCANNER SETTINGS ==========
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
SCAN_TIMEOUT = 10  # seconds

# ========== BEHAVIORAL MONITORING ==========
CPU_THRESHOLD = 80  # percent
MEMORY_THRESHOLD = 50  # percent
MONITOR_INTERVAL = 60  # seconds

# ========== QUARANTINE ==========
QUARANTINE_PASSWORD = b'malvryx_2024'

# ========== WEB SERVER ==========
WEB_HOST = '0.0.0.0'
WEB_PORT = int(os.environ.get('PORT', 5000))

# ========== LOGGING ==========
LOG_LEVEL = 'INFO'

# ========== PRINT STATUS ==========
if IS_RENDER:
    print("[*] Running on Render")
elif IS_VERCEL:
    print("[*] Running on Vercel")
else:
    print("[*] Running locally")
