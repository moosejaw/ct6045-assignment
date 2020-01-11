#!/usr/bin/env python3
'''
Listens for prediction data being sent from the real-time analytics model.
'''
import time
import pprint
import socket
from queue import Queue
from threading import Thread

DATA_QUEUE  = Queue()
MODEL_STATS = {'true_neg': 0, 'true_pos': 0, 'false_neg': 0, 'false_pos': 0}

def establishSocket():
    '''Establishes a socket to listen on.'''
    # Create the socket
    sock = socket.socket(sock.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 10025))
    sock.listen(500)
    conn, addr = sock.accept()
    return conn

def receiveData():
    '''Receives the incoming data from the real-time model and appends the
    data to a queue to be processed.'''
    conn = establishSocket()
    while True:
        data = conn.recv(3)
        if not data:
            conn = establishSocket()
        else:
            data = data.decode()
            DATA_QUEUE.append((int(data[0]), int(data[2])))

def processQueue():
    '''Processes the data in the queue.'''
    while True:
        if not DATA_QUEUE.empty():
            pred = DATA_QUEUE.get()
            if not pred[0] and not pred[1]:
                MODEL_STATS['true_neg'] += 1
            elif pred[0] and pred[1]:
                MODEL_STATS['true_pos'] += 1
            elif not pred[0] and pred[1]:
                MODEL_STATS['false_pos'] += 1
            elif pred[0] and not pred[1]:
                MODEL_STATS['false_neg'] += 1
            DATA_QUEUE.task_done()
        else: time.sleep(2)

def printStats():
    '''Prints the model statistic tally every 10 seconds.'''
    while True:
        time.sleep(10)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(MODEL_STATS)

if __name__ == '__main__':
    # Create threads for each task
    threads = []
    thr     = Thread(target=receiveData)
    threads.append(thr)
    thr.start()
    thr     = Thread(target=processQueue)
    threads.append(thr)
    thr.start()
    thr     = Thread(target=printStats)
    threads.append(thr)
    thr.start()
    for thread in threads: thread.join()
