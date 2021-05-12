#! /usr/bin/python3

import socket

HOST = "0.0.0.0"
PORT = 8000
MAX_CONNECTIONS = 64

APP_IP = "127.0.0.1"
APP_PORT = 8080

class TCPProxy:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to address
        soc.bind((HOST, PORT))
        # Set socket as listener
        soc.listen(MAX_CONNECTIONS)

    def handle_incoming():
        # Accept connection
        connection, address = soc.accept()
        print(f"Incoming connection from: {address}")

        # Handle connection
        rec_msg = connection.recv(1024)
        rec_msg = rec_msg.decode("utf-8")
        print(rec_msg)
        return rec_msg

    def 

# Create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    # Bind to address
    soc.bind((HOST, PORT))

    # Set socket as listener
    soc.listen(MAX_CONNECTIONS)

    # Infinitly keep accepting connections, handle and close
    while True:
        # Accept connection
        connection, address = soc.accept()
        print(f"Incoming connection from: {address}")

        # Handle connection
        rec_msg = connection.recv(1024)
        rec_msg = rec_msg.decode("utf-8")
        print(rec_msg)

        resp_msg = f"HTTP/1.1 200 OK\n<html>{rec_msg}</html>"
        connection.sendall(bytes(resp_msg, encoding="utf-8"))
        connection.sen

        # Close connection
        connection.close()