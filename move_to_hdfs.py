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
    commands = [
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-copyFromLocal',
        f'{CSV_DIR}',
        f'{HDFS_DATA_DIR}'
    ]
    proc = subprocess.Popen(commands)
    proc.communicate()

    print(f'Copied training and testing from {HDFS_DATA_DIR} to HDFS.')
