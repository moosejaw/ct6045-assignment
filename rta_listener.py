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

def getAccuracy(correct, total):
    if not correct or not total: return 0
    return correct / total

def getSensitivity(tp, fn):
    if not tp or not fn: return 0
    return tp / (tp + fn)

def getSpecificity(tn, fp):
    if not tp or not fp: return 0
    return tn / (tn + fp)

def establishSocket():
    '''Establishes a socket to listen on.'''
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bound = False
    while not bound:
        try:
            time.sleep(1)
            sock.bind(('localhost', 10025))
            bound = True
        except OSError: pass
    sock.listen(500)
    conn, addr = sock.accept()
    return conn

def receiveData():
    '''Receives the incoming data from the real-time model and appends the
    data to a queue to be processed.'''
    conn = establishSocket()
    while True:
        data = conn.recv(1024)
        if not data:
            conn = establishSocket()
        else:
            data = data.decode().split('X')
            for pkt in data:
                if pkt:
                    try:
                        DATA_QUEUE.put((int(pkt[0]), int(pkt[2])))
                    except (ValueError, IndexError):
                        pass

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
        time.sleep(15)
        tot = 0
        for i in MODEL_STATS.keys(): tot = tot + MODEL_STATS[i]
        acc = getAccuracy(MODEL_STATS["true_neg"] + MODEL_STATS["true_pos"],
            tot)
        sens = getSensitivty(MODEL_STATS["true_pos"], MODEL_STATS["false_neg"])
        spec = getSpecificity(MODEL_STATS["true_neg"], MODEL_STATS["false_pos"])
        print(f'''
        ------------
        Current Statistics:
        ------------
        True Negs.  : {MODEL_STATS["true_neg"]}
        True Pos.   : {MODEL_STATS["true_pos"]}
        False Pos.  : {MODEL_STATS["false_pos"]}
        False Negs. : {MODEL_STATS["false_neg"]}
        Total       : {tot}
        ------------
        Accuracy    : {acc}
        Sensitivity : {sens}
        Specificity : {spec}
        ------------
        \n
        ''')

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
