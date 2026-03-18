@echo off
echo Student Study Kit - Baslatiliyor...
echo.

:: Python kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo Python bulunamadi! Lutfen Python 3.8+ yukleyin.
    pause
    exit /b 1
)

:: Gereksinimleri kontrol et ve yukle
echo Gereksinimler kontrol ediliyor...
pip install -q PyQt6 pyaudio PyMuPDF playsound

:: Calistir
echo Uygulama baslatiliyor...
python main.py

pause
