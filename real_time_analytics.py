#!/usr/bin/env python3
'''
This script creates the regression model so that packets can be classified in
real time. You must carefully follow the instructions in README.md for this
model to work correctly.
'''
import os

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.classification import StreamingLogisticRegressionWithSGD

# Set HDFS locations - change to point to your HDFS address and port
HDFS_ADDR      = '127.0.0.1'
HDFS_PORT      = '54310'
TRAINING_DIR   = f'hdfs://{HDFS_ADDR}:{HDFS_PORT}/user/hduser/data/training'
STREAMING_DIR  = f'hdfs://{HDFS_ADDR}:{HDFS_PORT}/user/hduser/data/streaming'

# Model parameters
UPDATE_TIMER   = 5 # Update the model every x seconds

# The location of each column within the csv file when the header line is split
LABEL_INDEX    = 83
COLUMN_INDEXES = [34, 16, 18, 7, 24, 22, 23, 29, 27, 28, 26, 81, 79, 82]

def processTrainingLine(line):
    '''Returns a labelled point for RDDs based on the .csv files of the training
    data.'''
    return LabeledPoint(label=line.split(',')[0], features=line.split(',')[1:])

def processTestingLine(line):
    '''Returns a labelled point for RDDs based on the .csv files of the data
    being streamed to the model in HDFS.'''
    # Ignore the headers of files - send some dummy data for now
    if str(line[0]).isalpha(): return LabeledPoint(label=0.0, \
        features=[0.0 for i in range(len(column_map.keys()))])

    # Process the lines based on the columns we want to appear (hard-coded)
    line = line.split(',')
    return LabeledPoint(label=line[0], features=[line[i] for i in COLUMN_INDEXES])


if __name__ == '__main__':
    # First create the streaming context
    sc = SparkContext(appName="Realtime Packet Classifier")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, UPDATE_TIMER)

    # Create the data streams for the training and streaming directory
    trainingStream = ssc.textFileStream(TRAINING_DIR).map(processTrainingLine)
    testingStream  = ssc.textFileStream(STREAMING_DIR).map(processTestingLine)

    # Create the model and train it on the training data
    model = StreamingLogisticRegressionWithSGD()
    model.setInitialWeights([0 for i in range(len(COLUMN_INDEXES))])
    model.trainOn(trainingStream)

    # Get the model to predict on values incoming in the streaming directory
    model.predictOnValues(testingStream.map(lambda lp: (lp.label, lp.features))\
        ).pprint()

    # Start the stream and await manual termination
    ssc.start()
    ssc.awaitTermination()
