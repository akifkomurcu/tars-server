import urllib.request
import zipfile
import os

# RVC WebUI reposunu zip olarak indir (git yerine)
url = "https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/archive/refs/heads/main.zip"
zip_path = "rvc_webui.zip"

print("RVC WebUI indiriliyor...")
urllib.request.urlretrieve(url, zip_path)
print("Tamamlandi. Ayiklaniyor...")

with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall(".")

# Klasor adini rvc olarak yeniden adlandir
import shutil
if os.path.exists("rvc"):
    shutil.rmtree("rvc")
os.rename("Retrieval-based-Voice-Conversion-WebUI-main", "rvc")

os.remove(zip_path)
print("RVC klasoru hazir!")
