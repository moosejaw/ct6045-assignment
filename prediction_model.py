#!/usr/bin/env python3
'''
This scripts creates a Regression model, trained on the columns returned
from the `feature_reduction.py` script in order to classify whether packets
are BENIGN or MALICIOUS.
'''
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import StreamingLogisticRegressionWithSGD

import os
import pprint
import numpy as np
import pandas as pd
from modules.terminal_colour import Color

COLOUR      = Color()
OUTPUT_DIR  = 'output'
FEATUR_DIR  = os.path.join(OUTPUT_DIR, 'features')
COLUMNS     = 14 # All the numerical features we will use
CHUNK_SIZE  = 4096
SEED        = 12345
K           = 10 # Value of k used in k-fold validation

HDFS_ADDR       = '127.0.0.1:54310'
CHECKPOINT_DIR  = f'hdfs://{HDFS_ADDR}/user/hduser/checkpoint'
TRAINING_FOLDER = f'hdfs://{HDFS_ADDR}/user/hduser/data/csv/train/training_data.csv'
TESTING_FOLDER  = f'hdfs://{HDFS_ADDR}/user/hduser/data/csv/test'

def processLine(line):
    return LabeledPoint(label=line.split(',')[0], features=line.split(',')[1:])

if __name__ == '__main__':
    # Create spark context
    sc = SparkContext(appName="Packet Classifier")
    sc.setLogLevel("WARN")
    # Create the streaming context
    ssc = StreamingContext(sc, 1)

    # Read files from HDFS into stream
    training = sc.textFile('output/features/csv/train/training.csv').map(processLine)
    training = ssc.queueStream([training])

    # Create the model and train it on the training dataset
    print('Training the regression model...')
    model = StreamingLogisticRegressionWithSGD(numIterations=10)
    model.setInitialWeights([0 for i in range(COLUMNS)])
    model.trainOn(training)

    # Load the testing data
    testing = sc.textFile('output/features/csv/test/testing_data.csv').map(processLine)
    testing = ssc.queueStream([testing])

    # Now predict on the testing data
    print('Predicting on the testing data...')
    model.predictOnValues(testing.map(lambda lp: (lp.label, lp.features))).pprint()

    # Start ssc and await termination
    ssc.start()
    ssc.stop(stopSparkContext=True, stopGraceFully=True)

    # Once fit, we will test it on our holdout group and record the
    # TPs, TNs, FPs and FNs in a dict
    # COLOUR.setBlueText()
    # print('Checking predictions made on the holdout group...')
    # COLOUR.reset()
    # scorecard = {'true_pos': 0,
    #     'false_pos': 0,
    #     'true_neg': 0,
    #     'false_neg': 0,
    #     'len': 0}
    #
    # for test_row in data[group_i].collect():
    #     label = test_row.label
    #     pred  = model.predict(test_row.features)
    #     scorecard['len'] += 1
    #
    #     # Get whether the prediction was TP, FP, TN, FN
    #     if label == 0.0 and label == pred:
    #         scorecard['true_neg'] += 1
    #     elif label == 1.0 and label == pred:
    #         scorecard['true_pos'] += 1
    #     elif label == 0.0 and label != pred:
    #         scorecard['false_pos'] += 1
    #     else:
    #         scorecard['false_neg'] += 1
    #
    #     # Print the scorecard, append it to the scores array and move to
    #     # next iteration
    #     COLOUR.setBlueText()
    #     print(f'The scores for iteration {group_i} are:')
    #     pp = pprint.PrettyPrinter(indent=4)
    #     pp.pprint(scorecard)
    #     COLOUR.reset()
    #     scores.append(scorecard)
    #
    # # Now we'll get the sum of each score for each iteration and calculate
    # # the statistics
    # scorecard = {'true_pos': 0,
    #     'false_pos': 0,
    #     'true_neg': 0,
    #     'false_neg': 0,
    #     'len': 0}
    # for score in scores:
    #     for key in score.keys():
    #         scorecard[key] += score[key]
    #
    # # Print the overall scores
    # COLOUR.setGreenText()
    # pp = pprint.PrettyPrinter(indent=4)
    # print('The overall test results for the model are:')
    # pp.pprint(scorecard)
    # print('\n')
    #
    #     # Get the stats and print them
    #     acc = getAccuracy(scorecard['true_pos'] + scorecard['true_neg'],
    #         scorecard['len'])
    #     print(f'Accuracy    : {acc}')
    #     sens = getSensitivity(scorecard['true_pos'], scorecard['false_neg'])
    #     print(f'Sensitivity : {sens}')
    #     spec = getSpecificity(scorecard['true_neg'], scorecard['false_pos'])
    #     print(f'Specificity : {spec}')
    #     COLOUR.reset()
