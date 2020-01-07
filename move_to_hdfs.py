#!/usr/bin/env python3
'''
This script copies across every processed output script into HDFS on
localhost.
'''
import os
import subprocess

CSV_DIR        = os.path.join(os.path.join('output', 'features'), 'csv')
HADOOP_BIN_DIR = '/usr/local/hadoop/bin'
HDFS_DATA_DIR  = '/user/hduser/data'

if __name__ == '__main__':
    # Get files
    files = [os.path.join(CSV_DIR, file) for file in os.listdir(CSV_DIR) \
        if os.path.isfile(os.path.join(CSV_DIR, file)) \
        and file.endswith('_new.csv')]

    # Create the data_dir in hdfs
    proc = subprocess.Popen([
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-mkdir',
        '-p',
        HDFS_DATA_DIR
    ])
    proc.communicate()

    # Call a subprocess for each file, copying it across
    for file in files:
        hdfs_fname = file.split('/')
        hdfs_fname = hdfs_fname[len(hdfs_fname) - 1]
        commands = [
            f'{HADOOP_BIN_DIR}/hdfs',
            'dfs',
            '-copyFromLocal',
            f'{file}',
            f'{HDFS_DATA_DIR}/{hdfs_fname}'
        ]
        proc = subprocess.Popen(commands)
        proc.communicate()

    print(f'Copied all files from {HDFS_DATA_DIR} to HDFS.')
