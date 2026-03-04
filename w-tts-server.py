import os
import uuid
import asyncio
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import edge_tts

app = FastAPI(title="English TTS Server (Edge-TTS)")

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Mevcut US English sesler:
# en-US-GuyNeural        — erkek, doğal US aksanı
# en-US-JennyNeural      — kadın, doğal US aksanı
# en-US-AriaNeural       — kadın, konuşkan
# en-US-DavisNeural      — erkek, derin
# en-US-TonyNeural       — erkek, otoriter
VOICE = "en-US-GuyNeural"


class SpeechRequest(BaseModel):
    text: str
    voice: str = VOICE   # isteğe bağlı override


@app.post("/speak")
async def generate_speech(request: SpeechRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    output_filename = f"tts_{uuid.uuid4().hex}.mp3"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        print(f"🎙️  [{request.voice}] '{request.text[:80]}'")

        communicate = edge_tts.Communicate(text=request.text, voice=request.voice)
        await communicate.save(output_path)

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
            raise Exception("Audio file was not generated or is too small.")

        print(f"✅ Done: {output_filename} ({os.path.getsize(output_path):,} bytes)")

        return FileResponse(
            output_path,
            media_type="audio/mpeg",
            filename="speech.mp3"
        )

    except Exception as e:
        traceback.print_exc()
        if os.path.exists(output_path):
            os.remove(output_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voices")
async def list_voices():
    """Mevcut tüm US English seslerini listele"""
    voices = await edge_tts.list_voices()
    us_voices = [v for v in voices if v["Locale"].startswith("en-US")]
    return {"voices": [{"name": v["ShortName"], "gender": v["Gender"]} for v in us_voices]}


@app.get("/health")
async def health():
    return {"status": "ok", "engine": "edge-tts", "default_voice": VOICE}

# Başlatma: venv\Scripts\uvicorn.exe w-tts-server:app --host 0.0.0.0 --port 8000