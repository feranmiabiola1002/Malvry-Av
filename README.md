# ⚡ Malvryx AV - Next-Generation Antivirus Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Features

- **🔍 Real-Time Protection** - Monitors files and processes instantly
- **🧠 Hybrid Detection** - Signature + YARA + Behavioral Analysis
- **⚡ Lightweight** - Uses only 50MB RAM, <5% CPU
- **🔒 Zero Data Collection** - 100% private, no cloud uploads
- **🌐 Web Dashboard** - Monitor from any browser
- **📦 One-Click Installer** - Windows installer included
- **🔄 Auto-Updates** - Always up-to-date

## 📥 Installation

### One-Click Installer (Windows)
1. Download `MalvryxAV_Setup.exe` from [Releases](https://github.com/malvryx/malvryx-av/releases)
2. Double-click to install
3. Protection starts automatically!

### Manual Install (All Platforms)
```bash
git clone https://github.com/malvryx/malvryx-av.git
cd malvryx-av
pip install -r requirements.txt
python -m src.main init
python -m src.main watch
