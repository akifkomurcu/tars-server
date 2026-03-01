@echo off
cd /d "%~dp0"
echo Applio bagimliliklar kuruluyor...
venv\Scripts\pip.exe install ffmpeg-python faiss-cpu==1.13.2 librosa==0.11.0 scipy soundfile noisereduce pedalboard stftpitchshift soxr numba==0.63.1 torchcrepe torchfcpe einops transformers==4.44.2 matplotlib tensorboard gradio==6.5.1 tensorboardX edge-tts pypresence beautifulsoup4 sounddevice webrtcvad-wheels omegaconf wget tqdm requests -q
echo TAMAMLANDI!
pause
