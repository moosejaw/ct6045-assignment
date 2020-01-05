#!/usr/bin/env python3
'''
This script cleans up the raw dataset. It assumes that the .csv files are
located in the dataset/ folder. If they are located somewhere else, you can
modify the DATASET_PATH variable to point to the correct folder.

The columns which are retained are stored in an external Python module
which is imported and instantiated in this script. This is just to keep
this script more succinct. You can access the module and its values
by opening `modules/discriminator.py`
'''
import os
import numpy as np
import pandas as pd
from threading import Thread
import modules.common_functions
from modules.discriminator import Discriminator

DATASET_PATH = 'dataset/' # Change this variable if you need to
OUTPUT_PATH  = 'output/'
CHUNK_SIZE   = 1000000    # Files will be read in mutiple threads in 1MB chunks

def processColumnName(column):
    """
    Processes a column name from the .csv file, removing leading
    whitespace, removing capitalisation and replacing whitespace with
    an underscore.

    Inputs:
        - column: string containing the column name
    Outputs:
        string containing the processed column name
    """
    column = column.lower()
    column = column.strip()
    column = column.replace(' ', '_')
    return column

def processFile(path, cols, keep_cols):
    """
    Opens a .csv file and processes it in chunks.

    Args:
        - path: string representing the path to the file to be opened
        - cols: list of columns in the .csv file to be loaded into the dataframe
        - keep_cols: columns in the .csv file which won't be converted to floats
    """
    # Set the path for the converted file by replacing the
    # dataset path with the output path variable
    output_path = path.replace(DATASET_PATH, OUTPUT_PATH)

    # Generate a list of the columns to be converted to floats
    cols_to_convert = [modules.common_functions.processColumnName(col) for col \
        in cols if col not in keep_cols]

    # Go through each column and rename them
    renamed_cols = [modules.common_functions.processColumnName(col) for col \
        in cols]

    # Generate a list of columns to be kept as strings
    cols_as_strings = [col for col in renamed_cols if \
        col not in cols_to_convert]

    # As the .csv files are large we will read them in chunks,
    # process them on the fly and output them to new .csv files
    # as specified by the output_path variable
    with open(output_path, 'w') as output_file:
        for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=cols,
            encoding='latin'):
            # Rename the columns in the chunk by swapping the .columns attribute
            # with the list generated earlier
            chunk.columns = renamed_cols

            # Remove NaNs
            chunk = chunk.dropna()

            # Now convert the specified columns into floats
            for column in cols_to_convert:
                chunk[column] = chunk[column].astype(float)
            # Then the specified columns into strings
            for column in cols_as_strings:
                chunk[column] = chunk[column].astype(str)

            # Convert labels to 0 or 1 depending on whether or not they are
            # benign or malicious.
            # 0 -> benign and 1 -> malicious
            chunk['label'] = chunk['label'].map(lambda x: 0.0 if x == \
                'BENIGN' else 1.0)

            # Now write the processed output to the .csv file
            output_file.write(chunk.to_csv(index=False))
            continue

if __name__ == '__main__':
    print('Now processing the .csv files. This will take a while...')

    # Load the .csv files in the dataset folder into a list
    csv_files = [os.path.join(DATASET_PATH, i) for i in \
        os.listdir(DATASET_PATH) if \
        str(i).endswith('.csv')]

    # Create the output folder
    try:
        os.mkdir(OUTPUT_PATH)
    except FileExistsError:
        pass
    except OSError as e:
        print(f'Could not create a folder for the output {e}. Create the \
        folder manually and try again.')

    # Start a new thread for each .csv file and process them
    threads = []
    disc    = Discriminator()
    for file in csv_files:
        proc = Thread(target=processFile, args=[file,
            disc.columns,
            disc.columns_to_retain])
        proc.start()
        threads.append(proc)
    for thread in threads: thread.join()

    # Print message when all tasks are complete
    print(f'Done! The new .csv files have been output to {OUTPUT_PATH}.')
