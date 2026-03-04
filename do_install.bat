@echo off
chcp 65001 >nul
echo ============================================
echo  English TTS Server - Kurulum
echo ============================================
echo.

:: Python bul
set PYTHON_EXE=

py -3.11 --version >nul 2>&1
if %errorlevel%==0 ( set PYTHON_EXE=py -3.11 & goto :found )

py --version >nul 2>&1
if %errorlevel%==0 ( set PYTHON_EXE=py & goto :found )

for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
) do (
    if exist %%P ( set PYTHON_EXE=%%P & goto :found )
)

echo [HATA] Python bulunamadi!
echo https://www.python.org/downloads/ adresinden Python 3.11 kurun.
pause & exit /b 1

:found
echo [OK] Python bulundu: %PYTHON_EXE%

echo.
echo [1/3] Virtual environment olusturuluyor...
if exist venv (
    echo [OK] venv zaten mevcut, atlanıyor.
) else (
    %PYTHON_EXE% -m venv venv
)

echo.
echo [2/3] edge-tts kuruluyor...
venv\Scripts\pip.exe install --upgrade edge-tts

echo.
echo [3/3] FastAPI ve uvicorn kuruluyor...
venv\Scripts\pip.exe install fastapi uvicorn pydantic python-multipart

echo.
echo ============================================
echo  Kurulum TAMAMLANDI!
echo ============================================
echo.
echo Sunucuyu baslatmak icin:
echo   venv\Scripts\uvicorn.exe w-tts-server:app --host 0.0.0.0 --port 8000
echo.
pause
