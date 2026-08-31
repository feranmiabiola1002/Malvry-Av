#!/bin/bash
echo "========================================"
echo " Malvryx AV - Installer Builder"
echo "========================================"
echo
echo "[*] Installing PyInstaller..."
pip3 install pyinstaller
echo "[*] Building installer..."
pyinstaller --onefile --windowed --name "MalvryxAV_Setup" installer.py
echo
echo "[✓] Done! Check the 'dist' folder"
echo "    for MalvryxAV_Setup"
echo
