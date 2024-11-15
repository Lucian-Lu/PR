import socket
import errno
import sys
import threading
import time

# Function to receive messages from the other clients
def receive_messages(my_username):
    while True:
        time.sleep(1)
        try:
            # Getting the username from the server
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('\nConnection closed by the server')
                sys.exit()
            # Formatting the received data
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            # Outputting the message to the console
            print(f'\n{username} > {message}\n{my_username} > ', end='')

        # Closing the client socket in case of errors
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()


def send_messages():
    while True:
        message = input('')
        
        # If we have a message, we encode it and send it to the client socket
        if message:
            # Check if the message is "exit" to disconnect
            if message.lower() == "exit":
                print("Exiting the chat...")
                client_socket.close()
                sys.exit()
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)
            print(f'{my_username} > ', end='') 


HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connecting to the server
client_socket.connect((IP, PORT))
# Not blocking the server if a recv or send operation is performed
client_socket.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
# Sending the username over to the server for processing
client_socket.send(username_header + username)

t1 = threading.Thread(target=receive_messages, args=(my_username,))
t2 = threading.Thread(target=send_messages)

t1.start()
t2.start()
