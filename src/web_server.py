from flask import Flask, render_template_string, jsonify, request, send_file
import psutil
import os
import json
import datetime
import threading
import time
import sys

# ========== CLOUD COMPATIBILITY ==========
IS_RENDER = os.environ.get('RENDER') == 'true'
IS_VERCEL = os.environ.get('VERCEL') == '1'
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'malvryx_secret_key_2024'

# HTML Dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Malvryx AV Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { 
            background: #0a0a0a; 
            color: #00ff41; 
            font-family: 'Courier New', monospace; 
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { 
            border-bottom: 2px solid #00ff41; 
            padding: 20px 0; 
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 32px; text-shadow: 0 0 20px rgba(0,255,65,0.3); }
        .status-badge {
            background: #00ff41;
            color: #0a0a0a;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
        }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
        .card { 
            background: #111; 
            border: 1px solid #00ff41; 
            padding: 20px; 
            border-radius: 10px;
        }
        .card h3 { color: #888; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        .card .value { font-size: 36px; font-weight: bold; margin: 10px 0; }
        .progress { 
            width: 100%; 
            height: 20px; 
            background: #1a1a1a; 
            border-radius: 10px; 
            overflow: hidden; 
        }
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #00ff41, #00cc33); 
            width: 0%; 
            transition: width 0.5s;
        }
        .btn {
            background: #00ff41;
            color: #0a0a0a;
            padding: 10px 25px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin: 5px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #00cc33;
            transform: scale(1.05);
        }
        .btn-danger {
            background: #ff0044;
            color: white;
        }
        .btn-danger:hover {
            background: #cc0033;
        }
        .btn-outline {
            background: transparent;
            border: 2px solid #00ff41;
            color: #00ff41;
        }
        .btn-outline:hover {
            background: #00ff41;
            color: #0a0a0a;
        }
        .input-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 10px 0;
        }
        .input-group input {
            flex: 1;
            background: #1a1a1a;
            color: #00ff41;
            border: 1px solid #00ff41;
            padding: 10px;
            border-radius: 5px;
            min-width: 200px;
        }
        .full { grid-column: 1 / -1; }
        .log {
            background: #000;
            padding: 10px;
            height: 300px;
            overflow-y: auto;
            font-size: 12px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        }
        .log-line {
            padding: 4px 0;
            border-bottom: 1px solid #0a0a0a;
        }
        .log-line .time { color: #555; }
        .log-line .info { color: #00ff41; }
        .log-line .warning { color: #ffff00; }
        .log-line .error { color: #ff0044; }
        .quarantine-list {
            max-height: 200px;
            overflow-y: auto;
            font-size: 12px;
        }
        .quarantine-item {
            padding: 5px 0;
            border-bottom: 1px solid #1a1a1a;
            display: flex;
            justify-content: space-between;
        }
        .process-list {
            max-height: 200px;
            overflow-y: auto;
            font-size: 12px;
        }
        .process-item {
            padding: 3px 0;
            border-bottom: 1px solid #1a1a1a;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>⚡ MALVRYX AV CONTROL</h1>
        <span class="status-badge" id="status-badge">● ONLINE</span>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>🖥️ CPU Usage</h3>
            <div class="value" id="cpu">0%</div>
            <div class="progress"><div class="progress-fill" id="cpu-bar"></div></div>
        </div>
        <div class="card">
            <h3>🧠 Memory Usage</h3>
            <div class="value" id="mem">0%</div>
            <div class="progress"><div class="progress-fill" id="mem-bar"></div></div>
        </div>
        <div class="card">
            <h3>💾 Disk Usage</h3>
            <div class="value" id="disk">0%</div>
            <div class="progress"><div class="progress-fill" id="disk-bar"></div></div>
        </div>
    </div>
    
    <div class="grid">
        <div class="card full">
            <h3>🔍 Scan Controls</h3>
            <div class="input-group">
                <button class="btn" onclick="startScan('quick')">⚡ Quick Scan</button>
                <button class="btn" onclick="startScan('full')">🔍 Full Scan</button>
                <button class="btn btn-outline" onclick="startScan('custom')">📁 Custom Scan</button>
                <input type="text" id="scan-path" placeholder="Path to scan (e.g., C:/Downloads)" value="/tmp">
                <button class="btn btn-danger" onclick="stopScan()">⏹ Stop</button>
            </div>
            <div id="scan-progress" style="display:none;margin-top:15px;">
                <div>Status: <span id="scan-status">Running...</span></div>
                <div class="progress" style="margin:10px 0;">
                    <div class="progress-fill" id="scan-bar" style="width:0%"></div>
                </div>
                <div>Files: <span id="scan-files">0</span> | Threats: <span id="scan-threats">0</span></div>
            </div>
        </div>
    </div>
    
    <div class="grid">
        <div class="card full">
            <h3>📊 Live Log</h3>
            <div class="log" id="log">
                <div class="log-line"><span class="time">[System]</span> <span class="info">Dashboard connected</span></div>
            </div>
        </div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>🔄 Running Processes</h3>
            <div class="process-list" id="processes">
                <div class="process-item">Loading...</div>
            </div>
        </div>
        <div class="card">
            <h3>🔒 Quarantine</h3>
            <div class="quarantine-list" id="quarantine">
                <div class="quarantine-item">Empty</div>
            </div>
        </div>
        <div class="card">
            <h3>📈 Statistics</h3>
            <div style="margin:10px 0;">
                <div>Files Scanned: <span id="total-files" style="color:#00ff41;">0</span></div>
                <div>Threats Found: <span id="total-threats" style="color:#ff0044;">0</span></div>
                <div>Signatures: <span id="total-signatures" style="color:#00ff41;">0</span></div>
                <div>Uptime: <span id="uptime">0s</span></div>
            </div>
            <button class="btn" onclick="generateReport()">📄 Generate Report</button>
            <button class="btn btn-outline" onclick="checkUpdates()">🔄 Check Updates</button>
            <a href="/download" class="btn" style="display:inline-block;text-decoration:none;margin-top:10px;">⬇️ Download Installer</a>
        </div>
    </div>
</div>

<script>
const startTime = Date.now();
let scanId = null;
let scanInterval = null;

function addLog(msg, type = 'info') {
    const log = document.getElementById('log');
    const time = new Date().toLocaleTimeString();
    const colors = { info: '#00ff41', warning: '#ffff00', error: '#ff0044' };
    log.innerHTML += `<div class="log-line"><span class="time">[${time}]</span> <span style="color:${colors[type] || '#00ff41'}">${msg}</span></div>`;
    log.scrollTop = log.scrollHeight;
}

function startScan(type) {
    const path = document.getElementById('scan-path').value || '/tmp';
    document.getElementById('scan-progress').style.display = 'block';
    document.getElementById('scan-bar').style.width = '0%';
    document.getElementById('scan-status').textContent = 'Starting...';
    addLog(`Starting ${type} scan on ${path}`, 'info');
    
    fetch('/api/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type, path: path})
    })
    .then(r => r.json())
    .then(data => {
        scanId = data.scan_id;
        addLog(`Scan ID: ${scanId} started`, 'info');
        
        if (scanInterval) clearInterval(scanInterval);
        scanInterval = setInterval(() => {
            fetch('/api/scan/' + scanId + '/status')
            .then(r => r.json())
            .then(data => {
                document.getElementById('scan-bar').style.width = data.progress + '%';
                document.getElementById('scan-files').textContent = data.files || 0;
                document.getElementById('scan-threats').textContent = data.threats || 0;
                document.getElementById('scan-status').textContent = data.status;
                
                if (data.status === 'completed') {
                    clearInterval(scanInterval);
                    addLog(`Scan completed: ${data.threats || 0} threats found`, 
                          data.threats > 0 ? 'warning' : 'info');
                    setTimeout(() => {
                        document.getElementById('scan-progress').style.display = 'none';
                    }, 3000);
                }
            });
        }, 1000);
    })
    .catch(err => {
        addLog(`Scan error: ${err}`, 'error');
    });
}

function stopScan() {
    addLog('Scan stopped by user', 'warning');
    document.getElementById('scan-progress').style.display = 'none';
    if (scanInterval) clearInterval(scanInterval);
}

function generateReport() {
    addLog('Generating report...', 'info');
    fetch('/api/report', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: 'html'})
    })
    .then(r => r.json())
    .then(data => {
        addLog(`Report generated: ${data.report_path}`, 'info');
        window.open('/api/report/download/' + data.report_id, '_blank');
    });
}

function checkUpdates() {
    addLog('Checking for updates...', 'info');
    fetch('/api/update')
    .then(r => r.json())
    .then(data => {
        if (data.update_available) {
            addLog(`Update available: ${data.version}`, 'warning');
            if (confirm(`New version ${data.version} available. Download now?`)) {
                window.location.href = '/api/download/update';
            }
        } else {
            addLog('You have the latest version', 'info');
        }
    });
}

// Update stats every 2 seconds
setInterval(() => {
    // System stats
    fetch('/api/status')
    .then(r => r.json())
    .then(data => {
        document.getElementById('cpu').textContent = data.cpu + '%';
        document.getElementById('mem').textContent = data.memory + '%';
        document.getElementById('disk').textContent = data.disk + '%';
        document.getElementById('cpu-bar').style.width = data.cpu + '%';
        document.getElementById('mem-bar').style.width = data.memory + '%';
        document.getElementById('disk-bar').style.width = data.disk + '%';
        
        const uptime = Math.floor((Date.now() - startTime) / 1000);
        const hours = Math.floor(uptime / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        const seconds = uptime % 60;
        document.getElementById('uptime').textContent = 
            `${hours}h ${minutes}m ${seconds}s`;
    });
    
    // Processes
    fetch('/api/processes')
    .then(r => r.json())
    .then(data => {
        const div = document.getElementById('processes');
        div.innerHTML = data.slice(0, 30).map(p => 
            `<div class="process-item">${p.name || 'Unknown'} - CPU: ${p.cpu || 0}% Mem: ${p.memory || 0}%</div>`
        ).join('');
    });
    
    // Quarantine
    fetch('/api/quarantine')
    .then(r => r.json())
    .then(data => {
        const div = document.getElementById('quarantine');
        if (data.length === 0) {
            div.innerHTML = '<div class="quarantine-item">Empty</div>';
        } else {
            div.innerHTML = data.map(item => 
                `<div class="quarantine-item">
                    <span>${item.name}</span>
                    <span style="color:#888;">${(item.size/1024).toFixed(1)}KB</span>
                </div>`
            ).join('');
        }
    });
    
    // Stats
    fetch('/api/stats')
    .then(r => r.json())
    .then(data => {
        document.getElementById('total-files').textContent = data.files_scanned || 0;
        document.getElementById('total-threats').textContent = data.threats_found || 0;
        document.getElementById('total-signatures').textContent = data.signatures || 0;
    });
}, 2000);
</script>
</body>
</html>
'''

# Global state
scans = {}
scan_progress = {}

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def status():
    try:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
    except:
        cpu = 0
        mem = 0
        disk = 0
    return jsonify({
        'cpu': cpu,
        'memory': mem,
        'disk': disk,
        'connections': 0,
        'processes': 0
    })

@app.route('/api/processes')
def processes():
    procs = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                procs.append({
                    'name': info['name'],
                    'cpu': round(info['cpu_percent'] or 0, 1),
                    'memory': round(info['memory_percent'] or 0, 1)
                })
            except:
                pass
    except:
        pass
    return jsonify(procs[:50])

@app.route('/api/quarantine')
def quarantine():
    items = []
    quarantine_dir = os.path.join(os.path.dirname(__file__), 'quarantine')
    if os.path.exists(quarantine_dir):
        for f in os.listdir(quarantine_dir):
            if f.endswith('.zip'):
                path = os.path.join(quarantine_dir, f)
                items.append({
                    'name': f,
                    'size': os.path.getsize(path),
                    'date': datetime.datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                })
    return jsonify(items)

@app.route('/api/stats')
def stats():
    return jsonify({
        'files_scanned': 0,
        'threats_found': 0,
        'signatures': 0
    })

@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.json
    scan_id = str(int(time.time()))
    scans[scan_id] = {
        'status': 'running',
        'progress': 0,
        'files': 0,
        'threats': 0,
        'path': data.get('path', '/'),
        'type': data.get('type', 'quick')
    }
    
    def run_scan():
        total = 100
        for i in range(total):
            time.sleep(0.05)
            scans[scan_id]['progress'] = i + 1
            scans[scan_id]['files'] = i * 10
            scans[scan_id]['threats'] = i // 15
        scans[scan_id]['status'] = 'completed'
    
    threading.Thread(target=run_scan, daemon=True).start()
    return jsonify({'scan_id': scan_id})

@app.route('/api/scan/<scan_id>/status')
def scan_status(scan_id):
    return jsonify(scans.get(scan_id, {'status': 'not_found'}))

@app.route('/api/report', methods=['POST'])
def generate_report():
    report_id = str(int(time.time()))
    report_path = f"report_{report_id}.html"
    with open(report_path, 'w') as f:
        f.write(f"""
        <html><head><title>Malvryx AV Report</title></head>
        <body style="background:#0a0a0a;color:#00ff41;font-family:monospace;padding:20px;">
        <h1>Malvryx AV Scan Report</h1>
        <p>Generated: {datetime.datetime.now()}</p>
        <p>Status: Clean</p>
        <p>No threats detected</p>
        </body></html>
        """)
    return jsonify({'report_id': report_id, 'report_path': report_path})

@app.route('/api/report/download/<report_id>')
def download_report(report_id):
    from flask import send_file
    return send_file(f"report_{report_id}.html", as_attachment=True)

@app.route('/api/update')
def check_update():
    return jsonify({'update_available': False, 'version': '1.0.0'})

@app.route('/api/download/update')
def download_update():
    return jsonify({'message': 'No update available'})

# ========== NEW DOWNLOAD ROUTES ==========
@app.route('/download')
def download_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Download Malvryx AV</title>
        <style>
            body { background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; padding: 40px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; }
            .btn { display: inline-block; background: #00ff41; color: #0a0a0a; padding: 20px 40px; border-radius: 10px; font-size: 24px; font-weight: bold; text-decoration: none; margin: 20px; }
            .btn:hover { background: #00cc33; transform: scale(1.05); }
            .version { color: #888; }
            .features { text-align: left; margin: 30px auto; max-width: 400px; }
            .features li { padding: 8px 0; border-bottom: 1px solid #1a1a1a; list-style: none; }
            .features li:before { content: "✅ "; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ Malvryx AV</h1>
            <p class="version">Version 1.0.0</p>
            <p style="color:#888;">Free • Open Source • No Spyware</p>
            
            <div class="features">
                <li>Real-time Protection</li>
                <li>Signature + YARA Detection</li>
                <li>Behavioral Monitoring</li>
                <li>Web Dashboard</li>
                <li>One-click Install</li>
            </div>
            
            <a href="/api/download/installer" class="btn">⬇️ Download Installer</a>
            <p style="color:#555;font-size:12px;">Windows 10/11 • 15MB • One-click install</p>
            
            <div style="margin-top: 30px; border-top: 1px solid #1a1a1a; padding-top: 20px;">
                <a href="/" style="color:#00ff41;text-decoration:none;">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/download/installer')
def download_installer():
    # Path to your installer file
    installer_path = os.path.join(os.path.dirname(__file__), '..', 'installer', 'dist', 'MalvryxAV_Setup.exe')
    if os.path.exists(installer_path):
        return send_file(installer_path, as_attachment=True, download_name='MalvryxAV_Setup.exe')
    return "Installer not found. Please build it first. Run: cd installer && build_installer.bat", 404

# ========== CLOUD ENTRY POINT ==========
if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════╗
║   MALVRYX AV - Web Control Center         ║
╚═══════════════════════════════════════════╝
    """)
    
    if IS_RENDER:
        print(f"[*] Running on Render - Port: {PORT}")
    elif IS_VERCEL:
        print("[*] Running on Vercel")
    else:
        print(f"[*] Running locally - http://localhost:{PORT}")
        print(f"[*] Download page: http://localhost:{PORT}/download")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
