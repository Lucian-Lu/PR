import socket
import time

def start_file_client():
    HEADER_LENGTH = 10
    IP = "127.0.0.1"
    PORT = 1235

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))

    print("Connected to file server.")
    print("Available commands: write:<message>, read:<lines>, exit:")

    while True:
        command = input("Enter command: ").strip()

        if not command:
            print("Command cannot be empty.")
            continue

        client_socket.send(command.encode("utf-8"))

        if command.lower().startswith("exit"):
            print("Exiting...")
            break

        # Receive response and handle it immediately
        response = client_socket.recv(1024).decode("utf-8")
        print(f"Response from server: {response}")

        # Optionally add a sleep time to simulate client think time
        time.sleep(1)  # Adjust as needed for timing consistency

    client_socket.close()

if __name__ == "__main__":
    start_file_client()
