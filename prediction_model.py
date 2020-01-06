#!/usr/bin/env python3
'''
This scripts creates a Support Vector Machine, trained on the columns returned
from the `feature_reduction.py` script.
'''
from pyspark.ml.linalg import Vectors
from pyspark.sql import Row, SparkSession
from pyspark.ml.classification import LinearSVC

import os
import pprint
import numpy as np
import pandas as pd
from modules.terminal_colour import Color

COLOUR      = Color()
OUTPUT_DIR  = 'output'
FEATUR_DIR  = os.path.join(OUTPUT_DIR, 'features')
COLUMNS_TO_USE_FILE = os.path.join(FEATUR_DIR, 'top_features.txt')
CHUNK_SIZE  = 25000
SEED        = 12345
K           = 10 # Value of k used in k-fold validation

def getAccuracy(num_correct, num_wrong):
    '''Returns the accuracy from the given parameters.'''
    return 0

def getSensitivity(true_pos, false_neg):
    return true_pos / (true_pos + false_neg)

def getSpecificity(true_neg, false_pos):
    return true_neg / (true_neg + false_pos)

if __name__ == '__main__':
    # Create the spark session
    spark = SparkSession.builder\
       .appName("Packet Classifier")\
       .getOrCreate()
    sc    = spark.sparkContext
    sc.setLogLevel('ERROR')

    # Start by enumerating the files in the output directory
    files = [os.path.join(OUTPUT_DIR, i) for i in os.listdir(OUTPUT_DIR) \
        if os.path.isfile(os.path.join(OUTPUT_DIR, i)) and i.endswith('.csv')]

    # Load the columns we want to use into an array so we can tell pandas
    # which columns we want to use when loading the dataframes
    columns = []
    with open(COLUMNS_TO_USE_FILE, 'r') as f:
        for line in f: columns.append(line[:-1])
    columns.append('label') # Make sure to include the label too

    # Declare an RDD which will contain all of the data
    data = sc.parallelize([])

    # Iterate over each file in chunks, convert the chunk to a dataframe,
    # then to a formatted Row and append it to the RDD containing all the data.
    COLOUR.setBlueText()
    print('Collecting the dataset into an RDD...')
    COLOR.reset()
    for file in files:
       for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE, usecols=columns):
        chunk = chunk.reindex(columns=sorted(chunk.columns))
        rdd = sc.parallelize([Row(label=row['label'],
            features=Vectors.dense(row.drop(columns=['label']).to_numpy()\
                .tolist())) for i, row in chunk.iterrows()])
        data = sc.union([data, rdd])

    # Now for the k-fold validaton and creating the model.
    # We'll start by random-splitting our
    # RDD into k groups, as specified by the global varaible.
    #
    # All the splits are output into a list, so we can test the model
    # for each split we have made - i.e. k times. The other splits will be used
    # as the training data.
    COLOUR.setBlueText()
    print(f'Splitting the RDD into {K} groups as specified by K...\n')
    COLOR.reset()
    data = data.randomSplit(weights=[1/K for i in range(K)], seed=SEED)
    scores = []

    for group_i in range(len(data)):
        COLOUR.setBlueText()
        print(f'Training the model to be tested on group {group_i}...')
        COLOUR.reset()
        # We'll take splits[x] as the test data and use the rest as training
        train_data = sc.union([data[i] for i in range(len(data))\
            if i != group_i])

        # Declare an SVM and fit it to the training data
        model = LinearSVC().fit(train_data.toDF())

        # Once fit, we will test it on our holdout group and record the
        # TPs, TNs, FPs and FNs in a dict
        COLOUR.setBlueText()
        print('Checking predictions made on the holdout group...')
        COLOUR.reset()
        scorecard = {'true_pos': 0,
            'false_pos': 0,
            'true_neg': 0,
            'false_neg': 0,
            'len': 0}

        for test_row in data[group_i].collect():
            label = test_row.label
            pred  = model.transform(sc.parallelize([Row(\
                features=test_row.features)]).toDF()).head().prediction
            scorecard['len'] += 1

            # Get whether the prediction was TP, FP, TN, FN
            if label == 0.0 and label == pred:
                scorecard['true_neg'] += 1
            elif label == 1.0 and label == pred:
                scorecard['true_pos'] += 1
            elif label == 0.0 and label != pred:
                scorecard['false_pos'] += 1
            else:
                scorecard['false_neg'] += 1

            # Print the scorecard, append it to the scores array and move to
            # next iteration
            COLOR.setBlueText()
            print(f'The scores for iteration {group_i} are:')
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(scorecard)
            COLOR.reset()
            scores.append(scorecard)

        # Now we'll get the sum of each score for each iteration and calculate
        # the statistics
        scorecard = {'true_pos': 0,
            'false_pos': 0,
            'true_neg': 0,
            'false_neg': 0,
            'len': 0}
        for score in scores:
            for key in score.keys():
                scorecard[key] += score[key]

        # Print the overall scores
        COLOR.setGreenText()
        pp = pprint.PrettyPrinter(indent=4)
        print('The overall test results for the model are:')
        pp.pprint(scorecard)
        print('\n')

        # Get the stats and print them
        acc = getAccuracy(scorecard['true_pos'] + scorecard['true_neg'],
            scorecard['false_pos'] + scorecard['false_neg'])
        print(f'Accuracy    : {acc}')
        sens = getSensitivity(scorecard['true_pos'], scorecard['false_neg'])
        print(f'Sensitivity : {sens}')
        spec = getSpecificity(scorecard['true_neg'], scorecard['false_pos'])
        print(f'Specificity : {spec}')
        COLOR.reset()
