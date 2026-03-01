import platform
import os
import uuid
import subprocess
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="TARS Voice Server (Piper Edition)")

# OS Detection and Path Configuration
current_os = platform.system().lower()
if current_os == "windows":
    PIPER_BINARY = os.path.join(os.getcwd(), "piper_cli", "piper", "piper.exe")
else:
    # On Mac/Linux, assume 'piper' is installed in path or provide instructions
    PIPER_BINARY = "piper" 

MODEL_PATH = os.path.join(os.getcwd(), "TARS.onnx")

print("TARS Ses Modeli Sunucusu Basliyor... (Piper CLI)")

if current_os == "windows" and not os.path.exists(PIPER_BINARY):
    print(f"DIKKAT: piper.exe bulunamadi! Yolu kontrol edin: {PIPER_BINARY}")
elif current_os != "windows":
    # Check if piper is in PATH
    try:
        subprocess.run([PIPER_BINARY, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"BILGI: '{PIPER_BINARY}' komutu sistem yolunda bulunamadi. Mac üzerinde 'brew install piper-tts' gerekebilir.")
if not os.path.exists(MODEL_PATH):
    print(f"DIKKAT: Model bulunamadi! Yolu kontrol edin: {MODEL_PATH}")

class SpeechRequest(BaseModel):
    text: str

@app.post("/speak")
async def generate_speech(request: SpeechRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Metin boş olamaz.")

    output_filename = f"tars_cloned_{uuid.uuid4().hex}.wav"
    output_path = os.path.join(os.getcwd(), output_filename)
    
    try:
        # Metni piper.exe'ye standart girdi (stdin) olarak gönderiyoruz
        print(f"Sentezleniyor: '{request.text}' -> {output_filename}")
        
        process = subprocess.Popen(
            [PIPER_BINARY, "--model", MODEL_PATH, "--output_file", output_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        _, stderr_data = process.communicate(input=request.text)
        
        if process.returncode != 0:
            print(f"Piper Hatasi: {stderr_data}")
            raise Exception(f"Piper basarisiz oldu: {stderr_data}")
        
        if not os.path.exists(output_path):
            raise Exception("Piper çalisti ancak WAV dosyasi uretilemedi!")
            
        file_size = os.path.getsize(output_path)
        print(f"📁 Ses dosyasi oluşturuldu: {output_filename} ({file_size} bytes)")
        
        if file_size < 100:
            raise Exception(f"Ses dosyasi cok kucuk ({file_size} bytes)")
            
        return FileResponse(output_path, media_type="audio/wav", filename="tars_response.wav")
        
    except Exception as e:
        traceback.print_exc()
        print(f"❌ Sentezleme hatası: {e}")
        if os.path.exists(output_path):
            pass # debug amacli tutulabilir veya os.remove(output_path)
        raise HTTPException(status_code=500, detail=f"Ses sentezleme hatasi: {str(e)}")

# Uygulamayi baslat komutu: venv\Scripts\uvicorn.exe w-tts-server:app --host 0.0.0.0 --port 8000