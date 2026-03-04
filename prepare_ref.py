"""
tars_ref.wav hazırlayıcı
========================
tars.wav dosyasından ilk 8 saniyelik temiz TARS sesini keser
ve tars_ref.wav olarak kaydeder. XTTS v2 bu dosyayı speaker
referansı olarak kullanacak.

Çalıştır: python prepare_ref.py
"""

import wave
import os

INPUT = "tars.wav"
OUTPUT = "tars_ref.wav"
DURATION_SEC = 8  # ilk 8 saniye alınır

if not os.path.exists(INPUT):
    print(f"HATA: {INPUT} bulunamadı.")
    exit(1)

with wave.open(INPUT, "rb") as src:
    params = src.getparams()
    framerate = params.framerate
    n_frames = int(framerate * DURATION_SEC)
    available = params.nframes
    n_frames = min(n_frames, available)

    frames = src.readframes(n_frames)

with wave.open(OUTPUT, "wb") as dst:
    dst.setparams(params)
    dst.writeframes(frames)

actual_sec = n_frames / framerate
print(f"✅ Tamamlandı: {OUTPUT} ({actual_sec:.1f} saniye)")
print(f"   Orijinal dosya: {INPUT} ({available / framerate:.1f} saniye)")
print()
print("Şimdi sunucuyu başlatabilirsiniz:")
print("  venv\\Scripts\\uvicorn.exe w-tts-server:app --host 0.0.0.0 --port 8000")
