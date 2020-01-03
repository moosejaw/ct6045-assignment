#!/usr/bin/env python3
'''
This script produces graph outputs from the top-scoring IP addresses in
PageRank.

The output directories are specified in the OUTPUT_DIR variable.
'''
import os
import pprint
import numpy as np
import pandas as pd
from threading import Thread
import modules.common_functions
from modules.terminal_colour import Color

# Pyspark modules
from pyspark.sql import SparkSession, DataFrame
from graphframes import GraphFrame

COLOUR      = Color()
BASE_DIR    = 'output'
PR_DIR      = os.path.join(BASE_DIR, 'pageranks')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'graphs')
GRAPH_DIRS  = ['source_ip', 'destination_ip']
SAMPLING_ITERATIONS = 5
SAMPLE_SIZE = 5000
SEEDS       = [i for i in range(SAMPLING_ITERATIONS)]
GRAPH_DATA  = {k: [] for k in GRAPH_DIRS}

# Create the SparkSession
SPARK       = SparkSession.builder.appName('PacketRouteGraph').getOrCreate()

def getSampleFromFile(file, seed):
    '''Returns a sample dataframe from a given file.'''
    return pd.read_csv(file, encoding='latin', \
        usecols=['source_ip', 'destination_ip'])\
        .sample(n=SAMPLE_SIZE, random_state=seed)

def countRoutes(pr_file, data_files):
    # Start by loading the contents of the pagerank file into a list
    ips = []
    with open(pr_file, 'r') as f:
        for line in f: ips.append(line[:-1])

    # Get the column to be searched from the file path
    column = pr_file.split('/')
    column = column[len(column) - 1].split('.txt')[0]
    print(f'Getting unique packet routes for significant IPs in column {column}...')

    # Now we will create blank dict which will be populated with the
    # source_ip->source_port->dest_ip->dest_port as the key and the number
    # of times this path occurs within the samples as the corresponding value.
    #
    # The key is created by converting each matching row to a numpy array
    # and converting the key into a string with a '/' character separating each
    # column.
    counts_by_ip = {}

    # We'll need to open each file again and get the same samples we did before.
    for file in data_files:
        for seed in SEEDS:
            # Load the sample into a dataframe
            df = getSampleFromFile(file, seed)

            # Now, for each IP address returned from the PageRank script,
            # we'll count how many times each unique route occurs with the
            # IP in its respective column.
            #
            # The code below seems kind of messy and there's probably a better
            # way of doing it, but for now, it works...
            for ip in ips:
                if not counts_by_ip or ip not in counts_by_ip.keys():
                    counts_by_ip[ip] = {}
                iter_counts = {}
                df_filtered = df[df[column].str.contains(ip)]
                if not df_filtered.empty:
                    df_filtered = df_filtered.to_numpy()
                    for row in df_filtered:
                            key = ''
                            for col in row: key = f'{key}/{col}'
                            if key not in iter_counts:
                                iter_counts[key] = 1
                            else:
                                iter_counts[key] += 1

                    # Quickly consolidate the routes from the sample with the
                    # ones recorded in previous iterations
                    for k in iter_counts.keys():
                        if k in counts_by_ip[ip]:
                            counts_by_ip[ip][k] += iter_counts[k]
                        else: counts_by_ip[ip][k] = iter_counts[k]

    # Now get the top 5 paths of each IP address
    for ip in counts_by_ip.keys():
        top = modules.common_functions.getTopValues(counts_by_ip[ip], 5)
        COLOUR.setGreenText()
        pp = pprint.PrettyPrinter(indent=4)
        print(f'The most common routes for IP {ip} (as a {column}) are:')
        pp.pprint(top)
        COLOUR.reset()

        # Now we'll add these routes and their counts to the GRAPH_DATA variable
        # based on the column they belong to
        GRAPH_DATA[column].append(top)

def generateGraphs():
    '''
    This function takes the top routes found in the countRoutes function,
    for the source_ip and dest_ip columns and creates a graph of each one.

    Ultimately it will generate a list of the most significant target and
    attack IPs and Ports.

    This function utilises the built-in PageRank algorithm from GraphX to
    determine the significance of each route.
    '''
    for column_key in GRAPH_DATA.keys():
        print(f'\nGenerating graph for column {column_key}...')
        # Start by concatenating the route counts into one dict object
        routes = {}
        for dict in GRAPH_DATA[column_key]:
            for key in dict.keys():
                routes[key] = dict[key]

        # Now we'll extract each vertex (unique IP address) from the routes,
        # and we'll take the number of connections as the weight for the edge.
        #
        # We'll also have to assign an ID for each IP address and build an array
        # of edges where each route is represented with its corresponding weight
        verts = []
        edges = []
        ids   = {}
        id    = 1
        for key in routes.keys():
            weight = routes[key] # Get the weight from the dict value
            ips_from_route = (key.split('/')[1], key.split('/')[2])
            for ip in ips_from_route:
                # Create a new ID for the IP address if it hasn't appeared yet
                if not ip in [i[1] for i in verts]:
                    verts.append((id, ip)) # Add it to the vertex array too
                    ids[ip] = id
                    id += 1 # And increment the ID
            # Now get the route and add it to the edges array as a tuple of:
            # (src, dest, weight)
            edges.append((ids[ips_from_route[0]], ids[ips_from_route[1]],
                weight))

        # Next, we'll convert the verts and edges arrays into Spark dataframes
        # so that we can load them into GraphFrames
        verts = SPARK.createDataFrame(verts, ['id', 'ip_address'])
        edges = SPARK.createDataFrame(edges, ['src', 'dest', 'wgt'])

        # Then we'll create the GraphFrames object, look at the edges, verts
        # and degrees, then run PageRank.
        graph = GraphFrame(verts, edges)
        print('Graph vertices:')
        graph.vertices.show()
        print('Graph edges:')
        graph.edges.show()
        print('Graph degrees:')
        graph.degrees.show()

        pr = graph.pageRank(resetProbability=0.15, tol=0.01)
        print('Graph PageRank vertices:')
        pr.vertices.show()
        print('Graph PageRank edges:')
        pr.edges.show()

if __name__ == '__main__':
    # Turn off logs from pyspark to clean up output
    SPARK.context.setLogLevel('ERROR')

    # First, begin by creating new folders for the graph outputs
    try:
        os.mkdir(OUTPUT_DIR)
        for dir in GRAPH_DIRS:
            os.mkdir(os.path.join(OUTPUT_DIR, dir))
    except FileExistsError:
        pass
    except OSError as e:
        print(f'An error occured when trying to create new directories: {e}')

    # Now enumerate the files and load them into a list
    data_files = [os.path.join(BASE_DIR, i) for i in os.listdir(BASE_DIR) \
        if os.path.isfile(os.path.join(BASE_DIR, i))]
    pagerank_files = [os.path.join(PR_DIR, i) for i in os.listdir(PR_DIR) \
        if os.path.isfile(os.path.join(PR_DIR, i))]

    # Exit if PageRank script has not been run yet
    if not pagerank_files:
        raise Exception('''
        The PageRank files directory is empty. You should run pagerank.py first.
        ''')

    # To draw the graphs, we will open each file in separate threads,
    # which will search each .csv file for instances of the IP address in its
    # respective column. It will then get the full path of each packet
    # and count how many times this particular path was traversed throughout the
    # dataset.
    threads = []
    for pr_file in pagerank_files:
        proc = Thread(target=countRoutes, args=[pr_file, data_files])
        threads.append(proc)
        proc.start()
    for thread in threads: thread.join()

    # Now move onto create and display the actual graphs
    generateGraphs()
