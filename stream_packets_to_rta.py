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

if __name__ == '__main__':
    # Get some necessary user input
    print('Please enter the path where TCPDUMP_and_CICFlowMeter was cloned.\nFor example, this may be /home/users/you/TCPDUMP_and_CICFlowMeter if you cloned the repo to your home folder.')
    print('Enter the path here: ')
    repo_folder = input()

    # Get info from user inputs
    pcap_folder = os.path.join(repo_folder, 'pcap')
    csv_folder  = os.path.join(repo_folder, 'csv')

    # Search for new .csv files and stream them into HDFS.
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
                new_f = file.replace(':', '_')
                os.rename(file, new_f)
                new_f = file.split('/')
                new_hdfs_f = f[len(f) - 1]
                proc = subprocess.Popen([
                    f'{HADOOP_BIN_DIR}/hdfs',
                    'dfs',
                    '-copyFromLocal',
                    new_f,
                    f'{HDFS_STREAMING_DIR}/{new_hdfs_f}'
                ])
                proc.communicate()
                print(f'Copied {file} to HDFS.')

            # Remove the files after they are made
            for file in files: os.remove(file)
