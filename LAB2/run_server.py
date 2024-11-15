import socket
import select
import os
from django.core.management import execute_from_command_line
import threading
import time
import logging
import random


def start_chat_room():
    HEADER_LENGTH = 10

    IP = "0.0.0.0"
    PORT = 1234
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    sockets_list = [server_socket]
    clients = {}
    print(f'Chat room server is listening for connections on {IP}:{PORT}...', flush=True)

    def receive_message(client_socket):
        try:
            # Receiving the client username
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:
            # Forcefully closed or lost connections
            return False

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            # If the notified socket is the one being read, we accept the connections from clients
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                # If we don't receive a username/the client forcefully closes/loses connection, we don't append it to the socket list
                if user is False:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')), flush=True)
            # Otherwise, we accept client messages
            else:
                message = receive_message(notified_socket)
                if message is False:
                    # If the connection is closed, we remove the socket
                    print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')), flush=True)
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue

                user = clients[notified_socket]
                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}', flush=True)
                # Sending the message over to the clients
                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                        
        # If we have a socket exception, we remove it from the list
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]


# Simple server that reads and writes to a file
def start_file_server():
    HEADER_LENGTH = 10
    IP = "0.0.0.0"
    PORT = 1235
    # Defining the global variables
    global file, lock, logger, write_event

    lock = threading.Lock()
    write_event = threading.Event()
    FILE_PATH = "./Output_Files/RW_FILE.txt"
    file = open(FILE_PATH, 'r+')
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='logsystem.txt', encoding='utf-8', level=logging.DEBUG)

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
    sleep_time = random.randint(1, 7)
    logger.info(f"Write file sleep time: {sleep_time}")
    time.sleep(sleep_time)
    # Setting a global event to other threads to ensure that the write threads get executed first
    write_event.set()
    
    with lock:
        file.write(message + "\n")
        file.flush()
    # Clearing the event after finishing the write operation
    write_event.clear()

    logger.info("Write to file function executed successfully.")

def read_file_message(commands):
    sleep_time = random.randint(1, 7)
    logger.info(f"Read file sleep time: {sleep_time}")
    time.sleep(sleep_time)
    # Making the thread executing the event wait on the 
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


def start_django_server():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LAB2.settings')
    port = 8000
    print(f"Web server is running on {port}", flush=True)
    execute_from_command_line(['manage.py', 'runserver', f'0.0.0.0:{port}', '--noreload'])


if __name__ == "__main__":
    t1 = threading.Thread(target=start_django_server)
    t2 = threading.Thread(target=start_chat_room)
    t3 = threading.Thread(target=start_file_server)

    t1.start()
    t2.start()
    t3.start()