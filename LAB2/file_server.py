import socket
import threading
import time
import logging
import random

# Defining the global variables
lock = threading.Lock()
write_event = threading.Event()
FILE_PATH = "./Output_Files/RW_FILE.txt"
file = open(FILE_PATH, 'r+')
logger = logging.getLogger(__name__)
logging.basicConfig(filename='logsystem.txt', encoding='utf-8', level=logging.DEBUG)

write_count = 0  # To track how many write operations are currently active

def start_file_server():
    HEADER_LENGTH = 10
    IP = "0.0.0.0"
    PORT = 1235

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()

    logger.info(f'File server is listening for connections on {IP}:{PORT}...')
    print(f'File server is listening for connections on {IP}:{PORT}...', flush=True)

    while True:
        client_socket, client_address = server_socket.accept()
        logger.info(f"Accepted connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Function to handle the client
def handle_client(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode("utf-8").strip()
            if not message:
                break
            handle_request(message, client_socket)
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        client_socket.close()
        logger.info("Client disconnected.")

# Function to handle client requests
def handle_request(message, client_socket):
    split_message = message.split(':', 1)
    command = split_message[0].lower()
    data = split_message[1] if len(split_message) > 1 else None

    if command == 'read':
        logger.info("Client requested to read from the file.")
        lines = read_file_message(data)
        response = "\n".join(lines)
        logger.info(f"Sending read response: {response}")
        client_socket.send(response.encode("utf-8"))
    elif command == 'write':
        logger.info("Client requested to write to the file.")
        write_file_server(data)
        client_socket.send(b"Data written to file successfully.")
    else:
        logger.warning("Invalid command entered.")
        client_socket.send(b"Invalid command.")

# Function to write to the file
def write_file_server(message):
    global write_count
    write_count += 1

    sleep_time = random.randint(1, 7)
    logger.info(f"Write file sleep time: {sleep_time}")
    time.sleep(sleep_time)

    with lock:
        file.write(message + "\n")
        file.flush()

    logger.info("Write to file function executed successfully.")
    write_count -= 1
    if write_count == 0:
        logger.info("All write operations completed. Setting write_event.")
        write_event.set()

# Function to read from the file
def read_file_message(commands):
    sleep_time = random.randint(1, 7)
    logger.info(f"Read file sleep time: {sleep_time}")
    time.sleep(sleep_time)

    write_event.wait()

    lines = []
    try:
        commands = int(commands)
        
        with lock:
            file.seek(0)
            for _ in range(commands):
                line = file.readline()
                if not line:
                    break
                lines.append(line.strip())

        logger.info(f"Read from file executed successfully; lines = {lines}")
        return lines
    except ValueError as e:
        logger.error(f"Invalid conversion format for commands: {commands}. Error: {e}")
        return []

# Start the file server
start_file_server()
