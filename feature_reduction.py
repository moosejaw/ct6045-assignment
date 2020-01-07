#!/usr/bin/env python3
'''
This script collects samples of the data and performs inter-feature correlation
on the data in order to determine which features should be used in the model.

The code for generating the heatmaps/correlation matrices is adapted from:

Badr, W. (2019) 'Why Feature Correlation Matters... A lot!' (Online)
Available at: https://towardsdatascience.com/why-feature-correlation-matters-a-lot-847e8ba439c4
'''
import os
import pprint
import seaborn
import matplotlib
import numpy as np
import pandas as pd
from threading import Thread
import modules.common_functions
import matplotlib.pyplot as plt
from modules.terminal_colour import Color
from modules.discriminator import Discriminator
matplotlib.use('Agg')

OUTPUT_BASE_DIR     = 'output'
OUTPUT_DIR          = os.path.join(OUTPUT_BASE_DIR, 'features')
OUTPUT_MATRIX_DIR   = os.path.join(OUTPUT_DIR, 'matrix')
SAMPLING_ITERATIONS = 25
SAMPLE_SIZE         = 2500
CORRELATION_THRESH  = 0.6
CHUNK_SIZE          = 4096
COLOUR              = Color()
SEEDS               = [i for i in range(SAMPLING_ITERATIONS)]
COEFFICIENTS        = [] # Do not modify

TOTAL_MATRIX_FNAME  = 'full_matrix.png'
TOP_MATRIX_FNAME    = 'top_matrix.png'
TOP_FEATURES_FNAME  = 'top_features.txt'

def getColumnsToDrop():
    '''Returns the columns to not find coefficients for from the discriminator.'''
    d = Discriminator()
    return [modules.common_functions.processColumnName(i) for i in d.columns_to_retain]

def countStrongCorrelations(arr, threshold):
    '''Returns an integer representing the number of values in an array
    greater than or equal to a certain threshold.'''
    counts = 0
    for value in arr:
        if value >= threshold: counts +=1
    return counts

if __name__ == '__main__':
    # Start by creating the output directory
    try:
        os.mkdir(OUTPUT_DIR)
        os.mkdir(OUTPUT_MATRIX_DIR)
    except FileExistsError:
        pass
    except OSError as e:
        print(f'An error occured when trying to make the output directories: {e}')

    # Get data files
    files = [os.path.join(OUTPUT_BASE_DIR, file) for file in \
        os.listdir(OUTPUT_BASE_DIR) if \
        os.path.isfile(os.path.join(OUTPUT_BASE_DIR, file)) and \
        file.endswith('.csv')]
    columns = getColumnsToDrop()

    # Take samples of each file and load into one dataframe, then generate
    # a correlation matrix of each one.
    print(f'Sampling the data and generating correlation coefficients:')
    for seed in SEEDS:
        data = pd.DataFrame()
        for file in files:
            sample = pd.read_csv(file, encoding='latin')\
                .sample(n=SAMPLE_SIZE, random_state=seed).drop(columns=columns)
            data = pd.concat((data, sample))
        correlation_df = data.corr()
        COEFFICIENTS.append(correlation_df)

    # Now get the average coefficients from the samples
    print(f'From {SAMPLING_ITERATIONS} samples, the average coefficients are as follows:')
    avg_coefficients = pd.concat(COEFFICIENTS).groupby(level=0).mean()
    matrix_columns = sorted(avg_coefficients.columns)
    avg_coefficients = avg_coefficients.reindex(\
        columns=matrix_columns)
    print(avg_coefficients)

    # Plot the first matrix of each variable and its correlation coefficient
    fname = os.path.join(OUTPUT_MATRIX_DIR, TOTAL_MATRIX_FNAME)
    try:
        if os.path.isfile(fname): os.remove(fname)
        fig, ax = plt.subplots(figsize=[25, 25])
        seaborn.heatmap(avg_coefficients, vmax=1.0, vmin=-1.0, center=0,
            fmt='.2f', linewidths=0.5, square=True, annot=True)
        plt.savefig(fname)
    except OSError as e:
        print(f'An error occured while trying to save the matrix plot: {e}')

    # From the matrix output, we can see that generally, |0.6| and above
    # represents a strong correlation. From here we can apply a function
    # to the dataset which removes which are < |0.6|
    #
    # Then, for each feature we will determine the amount of correlations
    # it has with other featues which are above |0.6|
    high_corr_counts = {}
    for row in list(zip(avg_coefficients.columns, avg_coefficients.values)):
        feature = row[0]
        count = countStrongCorrelations([abs(i) for i in row[1]],
            CORRELATION_THRESH)
        high_corr_counts[feature] = count
    highest_correlated = modules.common_functions.getTopValues(high_corr_counts,
        15)

    COLOUR.setGreenText()
    pp = pprint.PrettyPrinter(indent=4)
    print(f'The top 10 features with the highest correlations are:')
    pp.pprint(highest_correlated)

    # Now we will re-create the correlation matrix but only using these specific
    # features and we'll see what it looks like
    top_coefficients = avg_coefficients.filter(highest_correlated.keys())\
        .filter(highest_correlated.keys(), axis=0)
    fname = os.path.join(OUTPUT_MATRIX_DIR, TOP_MATRIX_FNAME)
    try:
        if os.path.isfile(fname): os.remove(fname)
        fig, ax = plt.subplots(figsize=[14, 14])
        seaborn.heatmap(top_coefficients, vmax=1.0, vmin=-1.0, center=0,
            fmt='.2f', linewidths=0.5, square=True, annot=True)
        plt.savefig(fname)
    except OSError as e:
        print(f'An error occured while trying to save the top matrix plot: {e}')

    # Manually remove the fwd_header_length feature
    del highest_correlated['fwd_header_length']
    features = sorted([i for i in highest_correlated.keys()])
    features.insert(0, 'label')

    # Save the feature names we want to use to a file so it can be picked up by
    # the predictive analytics script
    try:
        with open(os.path.join(OUTPUT_DIR, TOP_FEATURES_FNAME), 'w') as f:
            for feature in features: f.write(f'{feature}\n')
    except Exception as e:
        print(f'An exception occurred when trying to save the top features to a file: {e}')

    # Re-save the training data in order to capture only the columns we want
    # to use
    print('The output files will now be saved with ONLY their respective features...')
    for file in files:
        new_fname = file.replace('.csv', '_new.csv')
        with open(new_fname, 'w') as output_file:
            for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, usecols=features):
                chunk = chunk.reindex(columns=features)
                new_fname.write(chunk.to_csv(index=False, header=False))
    print('All done!')
