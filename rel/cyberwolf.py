#! /usr/bin/python3

import socket
import time
import class_preprocessor
import class_validation
import config
from tensorflow.keras.models import load_model

# TCP server settings
host = config.read_value("host_address")
port = int(config.read_value("host_port"))
max_connections = int(config.read_value("max_connections"))

# Remote server settings
remote_address = config.read_value("remote_address")
rempote_port = int(config.read_value("remote_port"))

# Cyberwolf settings
class_preprocessor.load_ignorefile() # This command can be turned off
model_path = config.read_value("model_path")
model_name = config.read_value("model_name")
dataset_path = config.read_value("dataset_path")
request_path = config.read_value("request_path")


class TCPProxy:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to address
        self.soc.bind((host, port))
        # Set socket as listener
        self.soc.listen(max_connections)

        print(f"Listening for incoming connections on {host}:{port}")

    def close(self):
        self.soc.close()

    def handle_incoming(self):
        # Accept connection
        connection, address = self.soc.accept() # This operation blocks untill a connection is made
        print("#################### REQUEST ####################")
        print(f"Incoming connection from: {address[0]}:{address[1]}")
        self.incoming_con = connection

        # Handle connection
        rec_msg = connection.recv(20480)
        rec_msg = str(rec_msg,"utf-8")

        return rec_msg

    def handle_response(self, response):
        # Send all bytes back to caller
        self.incoming_con.sendall(bytes(response, "utf-8"))
        print("Returned response to caller")

    def deny_connection(self):
        # Deny the connection with peer
        self.incoming_con.sendall(bytes("CONNECTION DENIED", "utf-8"))
        print("Sent DENY message to caller")

    def handle_proxy(self, msg):
        # Open a connection to the proxy called ps
        with socket.socket() as ps:
            # Connect to the remote application
            ps.connect((remote_address, rempote_port))
            # Send message to the remote application
            ps.sendall(bytes(msg, "utf-8"))
            print(f"Proxying message of size: {len(msg)}")
            # Recv response from remote application
            response = self._recv_timeout(ps, timeout=1)
            print(f"Received response from proxy of size: {len(response)}")
            return response

    def _recv_timeout(self, ps, timeout=2):
        # Make socket non-blocking
        ps.setblocking(0)
        
        # Store data here
        total_data = []
        data = ""
        
        # Starting timer
        start = time.time()
        while 1:
            # If there already is data, break after timeout
            if total_data and time.time() - start > timeout:
                break
            
            # If there is no data yet, wait twice the timeout
            elif time.time() - start > timeout * 2:
                break
            
            # Recv bytes
            try:
                data = ps.recv(8192)
                if data:
                    total_data.append(str(data, "utf-8"))

                    # Reset the start timer
                    start = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        
        # join all parts to make final string
        return "".join(total_data)

def evaluate(model, msg):
    msg = msg.splitlines()
    features = class_preprocessor.preprocess(msg)
    values = class_validation.parse(msg)
    return class_validation.validate(model, values, features)


def main():
    model = load_model(f"{model_path}/{model_name}")
    tcp_proxy = TCPProxy()

    try:
        # Infinitly keep accepting connections, handle and close
        while True:
            # Handle incoming connections
            rec_msg = tcp_proxy.handle_incoming()

            # If evaluation goes well, respond normally
            if evaluate(model, rec_msg):
                # Proxy message to remote application
                proxy_response = tcp_proxy.handle_proxy(rec_msg)

                # Return response from remote to caller
                tcp_proxy.handle_response(proxy_response)
            else:
                tcp_proxy.deny_connection()

            # Close the peer connection
            tcp_proxy.incoming_con.close()
            print("#################################################")
    except Exception as ex:
        print(str(ex))
    finally:
        tcp_proxy.close()


if __name__ == "__main__":
    main()
