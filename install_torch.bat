@echo off
set VENV_PYTHON=venv\Scripts\python.exe
%VENV_PYTHON% -m pip uninstall -y torch torchvision torchaudio
%VENV_PYTHON% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
