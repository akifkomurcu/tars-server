import urllib.request
import zipfile
import os
import shutil

# Applio - Modern RVC fork, Python 3.11 uyumlu
# https://github.com/IAHispano/Applio
url = "https://github.com/IAHispano/Applio/archive/refs/heads/main.zip"
zip_path = "applio.zip"

print("Applio (RVC fork) indiriliyor...")
urllib.request.urlretrieve(url, zip_path)
print("Tamamlandi. Ayiklaniyor...")

with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall(".")

if os.path.exists("applio"):
    shutil.rmtree("applio")
os.rename("Applio-main", "applio")
os.remove(zip_path)

print("Applio klasoru hazir! -> applio/")
print("Icerik:")
for f in os.listdir("applio"):
    print(" -", f)
