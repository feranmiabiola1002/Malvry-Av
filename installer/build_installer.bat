@echo off
echo ========================================
echo  Malvryx AV - Installer Builder
echo ========================================
echo.
echo [*] Installing PyInstaller...
pip install pyinstaller
echo [*] Building installer...
pyinstaller --onefile --windowed --name "MalvryxAV_Setup" installer.py
echo.
echo [✓] Done! Check the 'dist' folder
echo     for MalvryxAV_Setup.exe
echo.
pause
