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

HADOOP_BIN_DIR        = '/usr/local/hadoop/bin'
HDFS_STAGING_DIR      = '/user/hduser/data/staging'
HDFS_STREAMING_DIR    = '/user/hduser/data/streaming'
HDFS_TRAINING_DIR     = '/user/hduser/data/training'
HDFS_SEC_TRAINING_DIR = '/user/hduser/data/sectraining'
TRAINING_CSV_DIR      = 'output/features/csv/training'

def createHDFSFolders():
    '''Creates the folders for the data in HDFS, and delete the pre-existing data.'''
    # Create the data_dir in hdfs
    proc = subprocess.Popen([
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-mkdir',
        '-p',
        f'{HDFS_TRAINING_DIR}'
    ])
    proc.communicate()

    # Create the second training directory
    proc = subprocess.Popen([
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-mkdir',
        f'{HDFS_SEC_TRAINING_DIR}'
    ])
    proc.communicate()

    # Create the streaming directory
    proc = subprocess.Popen([
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-mkdir',
        f'{HDFS_STREAMING_DIR}'
    ])
    proc.communicate()

    # Create the staging directory
    proc = subprocess.Popen([
        f'{HADOOP_BIN_DIR}/hdfs',
        'dfs',
        '-mkdir',
        f'{HDFS_STAGING_DIR}'
    ])
    proc.communicate()

    for dir in [HDFS_STAGING_DIR, HDFS_STREAMING_DIR, HDFS_TRAINING_DIR, \
        HDFS_SEC_TRAINING_DIR]:
        proc = subprocess.Popen([
            f'{HADOOP_BIN_DIR}/hdfs',
            'dfs',
            '-rm',
            f'{dir}/*.csv'
        ])
        proc.communicate()

def streamTrainingData():
    '''Copies the training data into HDFS so the model can train on it.'''
    files = [os.path.join(TRAINING_CSV_DIR, file) for file \
        in os.listdir(TRAINING_CSV_DIR) if \
        os.path.isfile(os.path.join(TRAINING_CSV_DIR, file)) \
        and file.endswith('.csv')]
    for file in files:
        f = file.split('/')
        f = f[len(f) - 1]
        proc = subprocess.Popen([
            f'{HADOOP_BIN_DIR}/hdfs',
            'dfs',
            '-copyFromLocal',
            file,
            f'{HDFS_STAGING_DIR}/{f}'
        ])
        proc.communicate()

        proc = subprocess.Popen([
            f'{HADOOP_BIN_DIR}/hdfs',
            'dfs',
            '-mv',
            f'{HDFS_STAGING_DIR}/{f}',
            HDFS_TRAINING_DIR
        ])
        proc.communicate()
    print('Streamed the training data into HDFS.')


if __name__ == '__main__':
    # Get some necessary user input
    print('Please enter the path where TCPDUMP_and_CICFlowMeter was cloned.\nFor example, this may be /home/users/you/TCPDUMP_and_CICFlowMeter if you cloned the repo to your home folder.')
    print('Leave the input blank and just hit ENTER if the repo is located at: /home/hduser/TCPDUMP_and_CICFlowMeter')
    print('Enter the path here: ')
    repo_folder = input()

    if not repo_folder: repo_folder = '/home/hduser/TCPDUMP_and_CICFlowMeter'

    # Get info from user inputs
    csv_folder  = os.path.join(repo_folder, 'csv')

    # Create the new directories in HDFS
    print('\nNow preparing HDFS. You may see messages saying folders already exist/are empty. If so, you can disregard them.')
    createHDFSFolders()

    print('\n\nType y/Y to stream the CIC training data into HDFS. Do this if the model is not yet trained. Just leave the input blank or type N if this is the case: ')
    train = input()
    if train.lower().startswith('y'): streamTrainingData()

    # Search for new .csv files and stream them into HDFS.
    print(f'\nWaiting for .csv files to be written to {csv_folder}...')
    training_data_count = 0
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
                new_hdfs_f = new_f.split('/')
                new_hdfs_f = new_hdfs_f[len(new_hdfs_f) - 1]
                proc = subprocess.Popen([
                    f'{HADOOP_BIN_DIR}/hdfs',
                    'dfs',
                    '-copyFromLocal',
                    new_f,
                    f'{HDFS_STAGING_DIR}/{new_hdfs_f}'
                ])
                proc.communicate()
                print(f'Wrote {new_f} to staging area in HDFS.')

                # Determine whether to stream training data into the model
                # The first x .csv files to arrive will be used as further training data
                #
                # This is not unresaonable as the generated files tend to
                # contain many observations
                if training_data_count < 8:
                    hdfs_final_dir = HDFS_SEC_TRAINING_DIR
                    training_data_count += 1
                else: hdfs_final_dir = HDFS_STREAMING_DIR

                proc = subprocess.Popen([
                    f'{HADOOP_BIN_DIR}/hdfs',
                    'dfs',
                    '-mv',
                    f'{HDFS_STAGING_DIR}/{new_hdfs_f}',
                    f'{hdfs_final_dir}'
                ])
                proc.communicate()
                print(f'Moved {new_f} to streaming directory.')
                if training_data_count < 8: print('This file was treated as training data.')

                # Remove the files from local after they are made
                os.remove(new_f)
