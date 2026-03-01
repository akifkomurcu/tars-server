import urllib.request
import zipfile
import os

url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
zip_path = "piper_windows.zip"

print(f"Downloading {url} ...")
urllib.request.urlretrieve(url, zip_path)
print("Download complete. Extracting...")

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("piper_cli")

print("Extraction complete in 'piper_cli' folder.")
