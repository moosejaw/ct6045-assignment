#!/usr/bin/env python3
'''
This Python script collects packets from the TCPDUMP_and_CICFlowMeter project,
checks for output and streams the files into HDFS to be read by the real-time
prediction model.
'''
import os
import time
import subprocess
from threading import Thread

HADOOP_BIN_DIR     = '/usr/local/hadoop/bin'
HDFS_STREAMING_DIR = '/user/hduser/data/streaming'

def streamFilesToHDFS(csv_folder):
    '''Searches for new .csv files and streams them into HDFS.'''
    while True:
        # Delay
        time.sleep(5)

        # Check the output .csv folder for new files
        files = [os.path.join(csv_folder, file) \
            for file in os.listdir(csv_folder) \
            if os.path.isfile(os.path.join(csv_folder, file)) \
            and file.endswith('.csv')]
        if files:
            for file in files:
                proc = subprocess.Popen([
                    f'{HADOOP_BIN_DIR}/hdfs',
                    'dfs',
                    '-copyFromLocal',
                    file,
                    f'{HDFS_STREAMING_DIR}/'
                ])
            proc.communicate()
            print(f'Copied {file} to HDFS.')

def runPacketSniffer(repo_folder, interface, pcap_folder):
    '''Runs the packet sniffing script, creating the files to be streamed to
    HDFS.'''
    proc = subprocess.Popen([
        f'{repo_folder}/capture_interface_pcap.sh',
        interface,
        pcap_folder
    ])
    proc.communicate()


if __name__ == '__main__':
    # Get some necessary user input
    print('Please enter the path where TCPDUMP_and_CICFlowMeter was cloned.\nFor example, this may be /home/users/you/TCPDUMP_and_CICFlowMeter if you cloned the repo to your home folder.')
    print('Enter the path here: ')
    repo_folder = input()

    print('\nNow enter the interface you want to listen on.\nThis should be the interface beginning with "br-" listed when running ifconfig.')
    print('Enter the interface here: ')
    interface = input()

    # Get info from user inputs
    pcap_folder = os.path.join(repo_folder, 'pcap')
    csv_folder  = os.path.join(repo_folder, 'csv')

    # Create the threads to run the sniffer and streamer simultaneously
    threads = []
    thr_1 = Thread(target=runPacketSniffer, args=[repo_folder, interface,
        pcap_folder])
    thr_2 = Thread(target=streamFilesToHDFS, args=[csv_folder])
    threads.append(thr_1)
    threads.append(thr_2)
    thr_1.start()
    thr_2.start()
    for thread in threads: thread.join()
