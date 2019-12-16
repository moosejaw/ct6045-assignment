#!/usr/bin/env python
import time
import random
from urllib import request

# Set the target as defined by the container name and port
TARGET   = 'http://target:80'
TIME_MIN = 5
TIME_MAX = 30

# This script is designed to emulate normal web traffic. Therefore, it will
# request the server page in a randomly-assigned interval. The request is sent
# as normal using Python's built-in urllib library. The request is opened and
# closed as normal.
if __name__ == '__main__':
    while True:
        # Pause for a random time in the given range
        time.sleep(random.randrange(TIME_MIN, TIME_MAX))
        # Open the request
        request.urlopen(TARGET)
        # Print to say the request was made
        print('Sent a request to the target.')
