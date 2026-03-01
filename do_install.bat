@echo off
echo Starting installation... > install_progress.txt
venv\Scripts\python.exe -m pip install TTS fastapi uvicorn >> install_progress.txt 2>&1
echo Installation finished with code %errorlevel% >> install_progress.txt
