#! /usr/bin/python3

import socket
import time

HOST = "0.0.0.0"
PORT = 8000
MAX_CONNECTIONS = 64

APP_IP = "127.0.0.1"
APP_PORT = 8080

class TCPProxy:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to address
        self.soc.bind((HOST, PORT))
        # Set socket as listener
        self.soc.listen(MAX_CONNECTIONS)

        print(f"Listening for incoming connections on {HOST}:{PORT}")

    def close(self):
        self.soc.close()

    def handle_incoming(self):
        # Accept connection
        connection, address = self.soc.accept() # This operation blocks untill a connection is made
        print("############################################")
        print(f"Incoming connection from: {address}")
        self.incoming_con = connection

        # Handle connection
        rec_msg = connection.recv(20480)
        rec_msg = str(rec_msg,"utf-8")

        return rec_msg

    def handle_response(self, response):
        # Send all bytes back to caller
        self.incoming_con.sendall(bytes(response, "utf-8"))
        print(f"Returned response to caller")

    def handle_proxy(self, msg):
        # Open a connection to the proxy called ps
        with socket.socket() as ps:
            # Connect to the remote application
            ps.connect((APP_IP, APP_PORT))
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



def main():
    tcp_proxy = TCPProxy()

    try:
        # Infinitly keep accepting connections, handle and close
        while True:
            # Handle incoming connections
            rec_msg = tcp_proxy.handle_incoming()

            # Proxy message to remote application
            proxy_response = tcp_proxy.handle_proxy(rec_msg)

            # Return response from remote to caller
            tcp_proxy.handle_response(proxy_response)

            # Close the peer connection
            tcp_proxy.incoming_con.close()

            print("############################################")
    except Exception as ex:
        print(str(ex))
    finally:
        tcp_proxy.close()


if __name__ == "__main__":
    main()
