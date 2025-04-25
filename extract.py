import sys
import struct
import os
import subprocess

def extract(combined_path):
    # Read combined file
    with open(combined_path, 'rb') as f:
        combined_data = f.read()
    
    # Extract image size from last 4 bytes
    if len(combined_data) < 4:
        print("Invalid file format")
        return
    
    image_size = struct.unpack('<I', combined_data[-4:])[0]
    
    # Validate extracted size
    if image_size > len(combined_data) - 4:
        print("Corrupted data: Invalid image size")
        return
    
    # Extract hidden executable
    exe_data = combined_data[image_size:-4]
    output_name = "extracted_exe.exe"
    
    # Write executable to disk
    with open(output_name, 'wb') as f:
        f.write(exe_data)
    
    # Make executable (Unix systems)
    os.chmod(output_name, 0o755)
    
    print(f"Extracted executable to {output_name}")
    
    # Security warning
    run = input("[!] WARNING: Running untrusted code is dangerous!\n"
                "Run the extracted file? (y/n): ").strip().lower()
    
    if run == 'y':
        if sys.platform.startswith('win'):
            subprocess.run([output_name], shell=True)
        else:
            subprocess.run([f'./{output_name}'])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: extract.py <combined_image>")
        sys.exit(1)
    extract(sys.argv[1])