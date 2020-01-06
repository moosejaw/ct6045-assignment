#!/usr/bin/env python3
'''
This script copies across every processed output script into HDFS on
localhost.
'''
import os
import subprocess

HADOOP_BIN_DIR = '/usr/local/hadoop/bin'
HDFS_DATA_DIR  = 'user/hduser/data'

if __name__ == '__main__':
    # Get files
    files = [os.path.join('output', file) for file in os.listdir('output') \
        if os.path.isfile(os.path.join('output', file)) \
        and file.endswith('.csv')]

    # Create the data_dir in hdfs
    proc = subprocess.Popen([
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-mkdir',
        '-p',
        HDFS_DATA_DIR
    ])

    # Call a subprocess for each file, copying it across
    for file in files:
        hdfs_fname = file.split('/')[1]
        commands = [
            f'{HADOOP_BIN_DIR}/hdfs',
            'dfs',
            '-copyFromLocal'
            f'./{file}',
            f'{HDFS_DATA_DIR}/{hdfs_fname}'
        ]
        proc = subprocess.Popen(commands)
        proc.communicate()

    print(f'Copied all files from {HDFS_DATA_DIR} to HDFS.')
