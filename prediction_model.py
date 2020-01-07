#!/usr/bin/env python3
'''
This scripts creates a Regression model, trained on the columns returned
from the `feature_reduction.py` script in order to classify whether packets
are BENIGN or MALICIOUS.
'''
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import SVMWithSGD
from pyspark.mllib.evaluation import BinaryClassificationMetrics

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

def processLine(line):
    return LabeledPoint(label=line.split(',')[0], features=line.split(',')[1:])

def getAccuracy(correct, total):
    return correct / total

def getSensitivity(tp, fn):
    return tp / (tp + fn)

def getSpecificity(tn, fp):
    return tn / (tn + fp)

if __name__ == '__main__':
    # Create spark context
    sc = SparkContext(appName="Packet Classifier")
    sc.setLogLevel("WARN")
    # Create the streaming context
    #ssc = StreamingContext(sc, 1)

    # Read files from HDFS into stream
    training = sc.textFile('output/features/csv/train/training_data.csv').map(processLine)

    # Create the model and train it on the training dataset
    print('Training the regression model...')
    model = SVMWithSGD()
    model.train(training)

    # Load the testing data
    testing = sc.textFile('output/features/csv/test/testing_data.csv').map(processLine)

    # Now predict on the testing data
    print('Predicting on the testing data...')
    evaluation = testing.map(lambda lp: (float(model.predict(lp.features)), lp.label))

    # Get the metrics from the model
    metrics = BinaryClassificationMetrics(evaluation)
    print(f'AUROC       : {metrics.areaUnderROC}')
    print(f'AUPRC       : {metrics.areaUnderPR}')

    # Once fit, we will test it on our holdout group and record the
    # TPs, TNs, FPs and FNs in a dict
    COLOUR.setBlueText()
    print('Checking predictions made on the testing data...')
    COLOUR.reset()
    scorecard = {'true_pos': 0,
        'false_pos': 0,
        'true_neg': 0,
        'false_neg': 0,
        'len': 0}

    for pair in evaluation.collect():
        label = pair[1]
        pred  = pair[0]
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

    # Print the overall scores
    COLOUR.setGreenText()
    pp = pprint.PrettyPrinter(indent=4)
    print('The overall results for the model are:')
    pp.pprint(scorecard)
    print('\n')

    # Get the stats and print them
    acc = getAccuracy(scorecard['true_pos'] + scorecard['true_neg'],
        scorecard['len'])
    print(f'Accuracy    : {acc}')
    sens = getSensitivity(scorecard['true_pos'], scorecard['false_neg'])
    print(f'Sensitivity : {sens}')
    spec = getSpecificity(scorecard['true_neg'], scorecard['false_pos'])
    print(f'Specificity : {spec}')
    COLOUR.reset()
