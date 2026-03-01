import os
import io

os.environ["PIPER_ESPEAKNG_DATA_DIRECTORY"] = r"C:\Program Files\eSpeak NG\espeak-ng-data"
from piper import PiperVoice

MODEL_PATH = "TARS.onnx"
CONFIG_PATH = "TARS.onnx.json"
TEXT = "Hello, I am TARS. My humor setting is at seventy five percent."

print(f"Espeak yolu: {os.environ.get('PIPER_ESPEAKNG_DATA_DIRECTORY')}")
print("Espeak calisiyor mu kontrol ediyoruz...")

try:
    voice = PiperVoice.load(MODEL_PATH, CONFIG_PATH, use_cuda=False)
    phonemes = voice.phonemize(TEXT)
    # Konsol encoding hatasindan kacmak icin fonemleri stringe cevirirken encode/decode yapiyoruz
    safe_phonemes = str(phonemes).encode('ascii', 'replace').decode('ascii')
    print(f"[{len(phonemes)} cumle ayrildi] Phonemeler: {safe_phonemes}")
    
    if phonemes == [['']]:
        print("DIKKAT: Espeak-ng duzgun calismiyor, bos fonem uretildi!")
        
    wav_file = io.BytesIO()
    voice.synthesize(TEXT, wav_file)
    wav_data = wav_file.getvalue()
    
    print(f"Sentezleme basarili. Uretilen WAV boyutu: {len(wav_data)} byte")

except Exception as e:
    print(f"HATA {type(e).__name__}: {str(e)}")
