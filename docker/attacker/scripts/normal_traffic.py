#!/usr/bin/env python3
This script is designed to emulate normal web traffic. Therefore, it will
request the server page in a randomly-assigned interval. The request is sent
as normal using Python's built-in urllib library. The request is opened and
closed as normal.
import time
import random
from urllib import request

# Set the target as defined by the container name and port
TARGET   = 'http://target/'
TIME_MIN = 5
TIME_MAX = 30

if __name__ == '__main__':
    # Wait a few seconds for the target container to spin up
    time.sleep(10)
    while True:
        # Pause for a random time in the given range
        time.sleep(random.randrange(TIME_MIN, TIME_MAX))
        # Open the request
        request.urlopen(TARGET)
        # Print to say the request was made
        print('Sent a request to the target.')
