#!/usr/bin/env python3
'''
This script runs the code behind the descriptive analytics section of the
assignment.

There are several things we look at here:

1. Firstly, we take a sample of a dataframe from each file. The sample size is
   specified in a global variable.

2. Second, we collect counts of each unique Source IP/Port and corresponding
   destination IP/Port and create a graph analysis of the top 5. The graph
   shows the travel of a packet from Source IP -> Source Port -> Dest IP ->
   Dest Port.

3. Thirdly, we run PageRank to discover the most influential sources and
   destinations. PageRank gathers a probabailistic eigenvector of the unique
   source/destination pairs and those with the highest probability are
   significant:
    - The source IP with the highest PageRank is most likely to be an attacker
    - The (internal) destination IP with the highest PageRank is most likely to
      be a target of an attack
'''
import os
import pprint
import random
import numpy as np
import pandas as pd
from threading import Thread
from modules.terminal_colour import Color

FILES_PATH          = 'output/'
COLUMNS_TO_PAGERANK = ['source_ip', 'destination_ip']
PAGERANK_RESULTS    = [] # Do not modify
SAMPLING_ITERATIONS = 5
SAMPLE_SIZE         = 5000
COLOUR              = Color()

def countConnections(df, column):
    '''
    Counts the total number of entries in a specified column, counted by entry.
    For example, 192.168.1.1 will be counted as many times as it appears within
    the specified column of the dataframe.

    Inputs:
    - df: DataFrame containing the data to be used
    - column: String containing the column to count connections (source/dest)
    Outputs:
    Tuple containing:
    - Dict containing the IP addresses as keys and the number of entries as
      the value
    - Integer representing the total number of entries
    '''
    # Start by declaring a blank dict and converting the specified column to an
    # array so it can be iterated over
    column_array = df[column].to_numpy()
    unique_ents  = set(column_array)
    counts  = {k: 0 for k in unique_ents}

    #COLOUR.setGreenText()
    #print(f'There are {len(unique_ents)} unique entries in the sample.')
    #COLOUR.reset()

    # Essentially, we have created a dictionary from the set of columns where
    # each column is its own key. Now we're iterating over the original array
    # and incrememnting the value at each key whenever it appears in the array.
    #
    # So what we'll see is something like:
    # {
    #  192.168.1.1: 43
    #  192.168.1.2: 35
    #  etc.
    # }
    for entry in column_array:
        counts[entry] += 1
    return counts

def getEigenvalue(total):
    '''
    Returns the eigenvalue of a total where Eigenvalue e = 1/n.
    '''
    return 1 / total

def getTopValues(d, size):
    '''
    Returns the largest key-value pairs in a given dict. Output is specified
    by the size arg.
    '''
    top = {}
    for key in d.keys():
        if not top or len(top.keys()) < size:
            top[key] = d[key]
        else:
            larger = False
            for k in top.keys():
                if d[key] > top[k]:
                    larger = True
            if larger:
                top[key] = d[key]
                del top[min(top, key=lambda x: top[x])]
                larger = False
    return top

def calculatePageRank(file, column):
    '''
    Calculates the PageRank for the unique entries in a given column.
    This function calls the other functions above it, as it is designed
    to be run in a thread.
    '''
    # Start by loading a sample of the file into a dataframe
    df = pd.read_csv(file, encoding='latin')\
        .sample(n=SAMPLE_SIZE)

    # For the source ip column, filter out traffic coming from our network
    # so that we can find the most suspicious external IPs
    if column == 'source_ip':
        df = df[~df[column].str.contains('192.168')]

    # Next, we need to get the count of each unique entry in the dataframe
    # for the specified column
    counts     = countConnections(df, column)
    df         = None # flush the df from memory
    eigenvalue = getEigenvalue(SAMPLE_SIZE)

    # No we'll multiply the eigenvalue across the count dict to determine
    # the PageRank for each key. We'll modify the count dict as it is.
    for key in counts.keys():
        counts[key] = counts[key] * eigenvalue

    # Now we'll take the top 10 PageRanks and add them to the PAGERANK_RESULTS
    # variable
    top = getTopValues(counts, 10)
    PAGERANK_RESULTS.append(top)

    #COLOUR.setGreenText()
    #print(f'PageRank for column: {column}')
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(top)
    #COLOR.reset()

def consolidatePageRanks(column):
    '''
    This function gets the highest overall values from the PageRank dicts
    contained in the PAGERANK_RESULTS global variable, which gets written to
    from the calculatePageRank function.

    The idea here is to gather each sample and select the top values from
    those.

    This function prints the top ten (unique) entries and their respective
    (average) eigenvector from each sample in which they appear.

    The output may not necessarily be of length 10 if one address was extremely
    significant in each factor. You could modify the random seed to try and
    change the outcome here.
    '''
    top_ten = {}
    avgs    = {}

    # Add each PageRank score and its value to a temporary dict
    for pr in PAGERANK_RESULTS:
        for key in pr.keys():
            if key not in avgs:
                avgs[key] = [pr[key]]
            else:
                avgs[key].append(pr[key])

    # Get the average PR for each one
    for pr in avgs.keys():
        avgs[pr] = sum(avgs[pr]) / len(avgs[pr])

    top_ten = getTopValues(avgs, 10)

    COLOUR.setGreenText()
    pp = pprint.PrettyPrinter(indent=4)
    print(f'The top average PR values from the samples of column {column} are:')
    pp.pprint(top_ten)
    COLOUR.reset()


if __name__ == '__main__':
    # Quick sanity check to make sure that the processed .csv files are in the
    # correct folder.
    try:
        os.listdir(FILES_PATH)
    except FileNotFoundError as e:
        COLOUR.setRedText()
        print(f'The directory specified at FILES_PATH is empty. ({e})')
        COLOUR.reset()
    except OSError as e:
        COLOUR.setRedText()
        print(f'The directory specified at FILES_PATH does not exist ({e})')
        COLOUR.reset()

    # Get all the files in the processed data directory
    files      = [os.path.join(FILES_PATH, i) \
        for i in os.listdir(FILES_PATH) \
        if os.path.isfile(os.path.join(FILES_PATH, i))
    ]

    # We will use the columns specified in the global variable to determine
    # which columns we want to perform PageRank on.
    # We'll perform PageRank for each one and get the top 5 from each.
    threads = []
    for column in COLUMNS_TO_PAGERANK:
        COLOUR.setBlueText()
        print(f'Calculating PageRank for column {column}...')
        COLOUR.reset()

        # Make threads to sample each file
        for iteration in range(SAMPLING_ITERATIONS):
            for file in files:
                proc = Thread(target=calculatePageRank,
                    args=[file, column])
                threads.append(proc)
                proc.start()
                for thread in threads: thread.join()
        consolidatePageRanks(column)
        PAGERANK_RESULTS = []
