#!/usr/bin/env python3
'''
As we are going to use a streaming model for our predictions, we will split our
dataset into "training" and "testing".

There is no easy way to do this so we will have to load each file into one
dataframe and perform the split from there. Then we can clean up by deleting
the original files.
'''
import os
import sklearn
import pandas as pd

SEED       = 12345
BASE_DIR   = os.path.join('output', 'features')
FILES_DIR  = os.path.join('output', 'csv')
TRAIN_DIR  = os.path.join(FILES_DIR, 'train')
TEST_DIR   = os.path.join(FILES_DIR, 'test')

TEST_DATA_FRAC = 0.30 # Fraction of training data will be 1 - this value

if __name__ == '__main__':
    print('This script will REMOVE the files output by feature_reduction.py. Press ENTER to continue...')
    input()

    try:
        os.mkdir(TRAIN_DIR)
        os.mkdir(TEST_DIR)
    except FileExistsError:
        pass

    data = pd.DataFrame()
    files = [os.path.join(FILE_DIR, file) for file in os.listdir(FILES_DIR) \
        if os.path.isfile(os.path.join(FILE_DIR, file)) \
        and file.endswith('_new.csv')]

    print('Splitting the data into training and testing...')
    for file in files:
        data = data.concat([data, pd.read_csv(file, header=None)])

    train, test = sklearn.model_selection.train_test_split(data,
        test_size=TEST_DATA_FRAC, random_state=SEED)

    # Save the training data to training dir
    print(f'Saving the training data to {TRAIN_DIR}...')
    with open(os.path.join(TRAIN_DIR, 'training_data.csv'), 'w') as f:
        f.write(train.to_csv(index=False, header=False))

    # Save the testing data to testing dir
    print(f'Saving the testing data to {TEST_DIR}...')
    with open(os.path.join(TEST_DIR, 'testing_data.csv'), 'w') as f:
        f.write(test.to_csv(index=False, header=False))

    # Remove the original files
    for file in files:
        os.remove(file)

    print('All done. You should now move these files to HDFS by running move_to_hdfs.py.')
