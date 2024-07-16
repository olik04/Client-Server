import socket
import os
import struct

server_ip = ""
server_port = 0
BUFFER_SIZE = 4096
CHUNK_SIZE = 256  # maximum length of the file


def post_string(sock):
    global server_ip, server_port
    cnt = 0  # count sent msg
    sock.sendall(b'POST_STRING')  # send command to server
    print("====== Content (Type a lone '&' to end message) ======")
    while True:
        line = input("client: ")
        sock.sendall(line.encode())
        cnt += 1
        if line == '&':  # end of the message
            break
    server_respond = str(sock.recv(BUFFER_SIZE).decode())
    if server_respond == 'server: OK':
        print(server_respond)  # print server response
        print(f"---\nSent {cnt} messages to (IP address:{server_ip}, port number:{server_port})")
        print("Connect status: OK\nSend status: OK\n---")
    else:
        print(server_respond)  # print server response
        print(f"---\nSent {cnt} messages to (IP address:{server_ip}, port number:{server_port})")
        print("Connect status: ERROR\nSend status: ERROR\n---")


def post_file(sock):
    global server_ip, server_port
    sock.sendall(b'POST_FILE\n')
    print(sock.recv(BUFFER_SIZE).decode())  # print server request for file path
    file_path = input("client:")
    try:
        filesize = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        # Pack file name and file size
        file_info = struct.pack('128sl', file_name.encode('utf-8'), filesize)
        sock.sendall(file_info)
        # Send data
        with open(file_path, 'rb') as f:
            print(f"Transfer file absolute path : {file_path}")  # print filepath if it is valid
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                sock.sendall(data)
    except FileNotFoundError:
        print("Cannot find the file")
        sock.sendall(b'close')
    finally:
        server_respond = sock.recv(BUFFER_SIZE).decode()
        print(server_respond)  # print server response
        if server_respond == "server: OK":
            print(f"(IP address:{server_ip}, port number:{server_port})")
            print("Connect status: OK\nSend status: OK")


def get(sock):
    global server_ip, server_port
    sock.sendall(b'GET\n')  # send command to server
    print("--- Received Messages ---")
    all_received = False  # boolean variable to show whether all messages were received
    get_msg = ""
    while not all_received:
        get_msg = sock.recv(BUFFER_SIZE).decode()
        get_msg = get_msg.replace("server: ", "")  # remove substring 'server: '
        print("client: " + get_msg, end='\n')  # print server response
        if get_msg == "&":  # End of the msg
            all_received = True
    if get_msg == "&":
        print(f"(IP address:{server_ip}, port number:{server_port})")
        print("Connect status: OK\nSend status: OK")
    else:
        print(f"(IP address:{server_ip}, port number:{server_port})")
        print("Connect status: ERROR\nSend status: ERROR")


def exit(sock):
    sock.sendall(b'EXIT\n')  # send command to server
    print(sock.recv(BUFFER_SIZE).decode())  # print server response


def main():
    # Initialize socket
    connection_unsuc = True
    client_socket = None
    while connection_unsuc:
        print("================== Initialize socket ==================")
        # IP and Port number of the server
        global server_ip, server_port
        server_ip = input("input IP address : ")
        if server_ip == 'localhost':
            server_ip = '127.0.0.1'
        server_port = int(input("input port number: "))
        # create a client socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the server
        try:
            # attempt to connect to the server
            client_socket.connect((server_ip, server_port))
            # print("Connection to server succeeded.")
        except socket.error:
            print("Error: connection is not built, try again")
        else:
            connection_unsuc = False

    # Input command
    print("==================== Input command ====================")
    while True:
        command = input("Input command:")
        if command == "POST_STRING":
            post_string(client_socket)
            print("==================== next command ====================")
        elif command == "POST_FILE":
            post_file(client_socket)
            print("==================== next command ====================")
        elif command == "GET":
            get(client_socket)
            print("==================== next command ====================")
        elif command == "EXIT":
            exit(client_socket)
            break
        else:
            client_socket.sendall(command.encode() + b'\n')
            print(client_socket.recv(BUFFER_SIZE).decode())
    client_socket.close()


if __name__ == "__main__":
    main()
