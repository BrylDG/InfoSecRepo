import sys
import os
import io
import base64
from PIL import Image
import subprocess
import tempfile

def embed_script_in_image(input_image_path, script_path, output_image_path):
    """
    Embeds a Python script within an image and creates a self-extracting image.
    When opened, it will display the image and run the embedded script.
    """
    try:
        # Read the original image
        img = Image.open(input_image_path)
        
        # Read the script to embed
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Convert script to base64 for embedding
        script_b64 = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
        
        # Create a copy of the image with embedded metadata
        img.info['embedded_script'] = script_b64
        
        # Save as a new image file
        img.save(output_image_path)
        
        print(f"Successfully embedded {script_path} in {output_image_path}")
        print("\nWARNING: This creates an executable image file. Only share with trusted sources.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def create_self_extracting_image(input_image_path, script_path, output_image_path):
    """
    Creates a self-extracting image that will:
    1. Display the original image when opened
    2. Execute the embedded script
    """
    try:
        # Read the original image as binary
        with open(input_image_path, 'rb') as f:
            image_data = f.read()
        
        # Read the script to embed
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # Create a Python stub that will extract and run the script
        stub_code = f'''#!/usr/bin/env python3
import os
import sys
import base64
import tempfile
from PIL import Image
import subprocess

# Embedded image data
image_data = {image_data}

# Embedded script
script_b64 = """{base64.b64encode(script_content.encode('utf-8')).decode('utf-8')}"""

# Display the image
temp_img = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
temp_img.write(image_data)
temp_img.close()

img = Image.open(temp_img.name)
img.show()

# Execute the embedded script
try:
    script = base64.b64decode(script_b64).decode('utf-8')
    temp_script = tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w')
    temp_script.write(script)
    temp_script.close()
    
    # Execute the script in a new process
    if sys.platform == 'win32':
        subprocess.Popen(['python', temp_script.name], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(['python3', temp_script.name])
    
    # Schedule cleanup (won't work on all systems)
    try:
        os.unlink(temp_img.name)
        os.unlink(temp_script.name)
    except:
        pass
        
except Exception as e:
    print(f"Error executing embedded script: {{e}}")
    input("Press Enter to exit...")
'''
        # Save as a Python executable
        with open(output_image_path, 'w', encoding='utf-8') as f:
            f.write(stub_code)
        
        # Make executable on Unix-like systems
        if sys.platform != 'win32':
            os.chmod(output_image_path, 0o755)
        
        print(f"Created self-extracting image: {output_image_path}")
        print("Note: The output is actually a Python script with the .png extension")
        print("To use: rename to .py or run as 'python output_image.png'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("Steganographic Script Embedder - Educational Purposes Only")
    print("1. Embed script in image (basic)")
    print("2. Create self-extracting image (displays image and runs script)")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == '1':
        input_image = input("Enter path to original image: ").strip('"')
        script_to_embed = input("Enter path to Python script to embed: ").strip('"')
        output_image = input("Enter path for output image: ").strip('"')
        
        if not all([input_image, script_to_embed, output_image]):
            print("Error: All paths are required")
            return
            
        embed_script_in_image(input_image, script_to_embed, output_image)
        
    elif choice == '2':
        input_image = input("Enter path to original image: ").strip('"')
        script_to_embed = input("Enter path to Python script to embed: ").strip('"')
        output_image = input("Enter path for output image: ").strip('"')
        
        if not all([input_image, script_to_embed, output_image]):
            print("Error: All paths are required")
            return
            
        create_self_extracting_image(input_image, script_to_embed, output_image)
        
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()