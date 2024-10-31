import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

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
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
        # Otherwise, we accept client messages
        else:
            message = receive_message(notified_socket)
            if message is False:
                # If the connection is closed, we remove the socket
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            # Sending the message over to the clients
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    
    # If we have a socket exception, we remove it from the list
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]