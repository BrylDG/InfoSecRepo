import base64
import re
import PyInstaller.__main__

def embed_files():
    # Ask for the image file path
    image_path = input("Enter path to the image file: ").strip('"')
    
    # Convert image to base64
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Ask for the script file path
    script_path = input("Enter path to the Python script to run in background: ").strip('"')
    
    # Read the script content and properly escape it
    with open(script_path, "r", encoding='utf-8') as script_file:
        script_content = script_file.read()
    
    # Clean the script content - escape triple quotes and fix indentation
    script_content = script_content.replace('"""', r'\"\"\"')
    script_content = re.sub(r'^ +', '', script_content, flags=re.MULTILINE)
    
    # Read the template script
    with open("embedded_app_template.py", "r", encoding='utf-8') as template_file:
        template_content = template_file.read()
    
    # Replace placeholders with actual content
    final_script = template_content.replace('"PLACEHOLDER_FOR_IMAGE"', f'"""{image_base64}"""')
    final_script = final_script.replace('"PLACEHOLDER_FOR_SCRIPT"', f'"""{script_content}"""')
    
    # Write the final script
    with open("embedded_app_final.py", "w", encoding='utf-8') as final_file:
        final_file.write(final_script)
    
    # Package with PyInstaller
    print("Building EXE...")
    PyInstaller.__main__.run([
        'embedded_app_final.py',
        '--onefile',
        '--windowed',
        '--name=EmbeddedApp'
    ])
    
    print("EXE created successfully!")

if __name__ == "__main__":
    embed_files()