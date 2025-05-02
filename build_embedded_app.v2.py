import base64
import re
import PyInstaller.__main__

def embed_files():
    # Ask for the image file path
    image_path = input("Enter path to the image file: ").strip('"')
    
    # Convert image to base64 with correct padding
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        padding = len(image_base64) % 4
        if padding:
            image_base64 += '=' * (4 - padding)
    
    print(f"[INFO] Embedded image file: {image_path}")
    
    # Ask for the script file path
    script_path = input("Enter path to the Python script to run in background: ").strip('"')
    
    with open(script_path, "r", encoding='utf-8') as script_file:
        script_content = script_file.read()
    
    # Clean the script content - escape triple quotes and fix indentation
    script_content = script_content.replace('"""', r'\"\"\"')
    script_content = re.sub(r'^ +', '', script_content, flags=re.MULTILINE)
    
    print(f"[INFO] Embedded background script: {script_path}")
    
    # Read the template script
    with open("embedded_app_template.py", "r", encoding='utf-8') as template_file:
        template_content = template_file.read()
    
    # Replace placeholders with actual content
    final_script = template_content.replace('"PLACEHOLDER_FOR_IMAGE"', f'"""{image_base64}"""')
    final_script = final_script.replace('"PLACEHOLDER_FOR_SCRIPT"', f'"""{script_content}"""')
    
    # Write the final script
    with open("embedded_app_final.py", "w", encoding='utf-8') as final_file:
        final_file.write(final_script)
    
    print("[INFO] Embedded app script written to embedded_app_final.py")
    
    # Package with PyInstaller
    print("[INFO] Building EXE with PyInstaller...")
    PyInstaller.__main__.run([
        'embedded_app_final.py',
        '--onefile',
        '--windowed',
        '--name=EmbeddedApp'
    ])
    
    print("[SUCCESS] EXE created successfully as EmbeddedApp.exe!")

if __name__ == "__main__":
    embed_files()
