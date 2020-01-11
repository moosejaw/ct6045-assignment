#!/usr/bin/env python3
'''
This scripts creates a Regression model, trained on the columns returned
from the `feature_reduction.py` script in order to classify whether packets
are BENIGN or MALICIOUS.
'''
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionWithSGD
from pyspark.mllib.evaluation import BinaryClassificationMetrics

import os
import pprint
import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt
from modules.terminal_colour import Color

COLOUR      = Color()
OUTPUT_DIR  = 'output'
BASE_DIR    = os.path.join(OUTPUT_DIR, 'generated')
TRAIN_DIR   = os.path.join(BASE_DIR, 'training')
TEST_DIR    = os.path.join(BASE_DIR, 'testing')
COLUMNS     = 14 # All the numerical features we will use
CHUNK_SIZE  = 4096
SEED        = 12345
K           = 10 # Value of k used in k-fold validation
ROC_OUTPUT  = os.path.join('output', 'roc_curve.png')

# The location of each column within the csv file when the header line is split
LABEL_INDEX    = 83
SRC_IP_COL     = 1
COLUMN_INDEXES = [34, 16, 18, 7, 24, 22, 23, 29, 27, 28, 26, 81, 79, 82]
MALICIOUS_IPS  = ['172.19.0.5', '172.19.0.4']

def processLine(line):
    return LabeledPoint(label=line.split(',')[0], features=line.split(',')[1:])

def processGeneratedLine(line):
    '''Returns a labelled point for RDDs based on the .csv files of the data
    being streamed to the model in HDFS.'''
    # Ignore the headers of files - send some dummy data for now
    if str(line[0]).isalpha(): return LabeledPoint(label=0.0, \
        features=[0.0 for i in range(len(line[7:82]))])

    # Process the lines based on the columns we want to appear (hard-coded)
    line = line.split(',')
    lbl  = 1.0 if line[SRC_IP_COL] in MALICIOUS_IPS else 0.0
    return LabeledPoint(label=lbl, \
        features=[float(i) for i in line[7:82]])

def getAccuracy(correct, total):
    return correct / total

def getSensitivity(tp, fn):
    return tp / (tp + fn)

def getSpecificity(tn, fp):
    return tn / (tn + fp)

if __name__ == '__main__':
    # Create spark context
    sc = SparkContext(appName="Packet Classifier")
    sc.setLogLevel("ERROR")
    # Create the streaming context
    #ssc = StreamingContext(sc, 1)

    # Read files from HDFS into stream
    training = sc.textFile('output/generated/training/a.csv').map(processGeneratedLine)

    # Create the model and train it on the training dataset
    print('Training the regression model...')
    model = LogisticRegressionWithSGD.train(training, intercept=True, iterations=5000)

    # Load the testing data
    testing = sc.textFile('output/generated/testing/b.csv').map(processGeneratedLine)

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

    y_true = []
    y_pred = []
    for pair in evaluation.collect():
        label = pair[1]
        pred  = pair[0]
        y_true.append(label)
        y_pred.append(pred)
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

    # Plot the ROC
    print('Plotting the ROC curve...')
    fpr, tpr, thresholds = roc_curve(y_true, y_pred, pos_label=1.0)
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2,
        label='AUC: %.2f' % metrics.areaUnderROC)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC Curve for trained logistic regression model')
    plt.legend(loc='lower right')
    plt.savefig(ROC_OUTPUT)
    print(f'Saved the figure to {ROC_OUTPUT}.')
