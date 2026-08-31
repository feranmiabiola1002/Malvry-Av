from flask import Flask, render_template_string, jsonify, request
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
            <h3>💾 Disk Usage
