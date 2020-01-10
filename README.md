# Introduction
This repository contains the supplementary code for the CT6045 assignment. Instructions on how to run each piece of code are available in this file. You should read each section of this file in order, as one section may depend on you having run another piece of code from a previous section.

# Pre-requisites
## Apache Hadoop
Apache Hadoop must be present on your system. A version of Apache Hadoop compatible with this project can be installed automatically by following the instructions of [this repository.](https://github.com/moosejaw/hadoop-ansible-installer)

## Apache Spark
You must ensure that you have Apache Spark 2.4 installed. It can be downloaded [here.](https://spark.apache.org/downloads.html)

## Installing Python requirements
There are several Python requirements which this project needs in order to run. You can download them all at once by simply running:

```bash
pip3 install -r requirements.txt
```

And the requirements should be installed for you automatically.

# Preparing the dataset
You should ensure that the dataset is present in a `dataset/` folder in the root of this project directory.

First, you need to run `preprocessing.py`. This is a Python script which processes each file in multiple threads. Comments about specific functionality are available in the Python script itself.

You can run the script by ensuring it has execute permissions and running:
```bash
./preprocessing.py
```

You should see a message saying `Done!` if the script has executed successfully.

The newly-processed `.csv` files are located in a folder named `output/` relative to the root of this project directory.

# Descriptive analytics
## Running descriptive analytics
**You must do this after you have run `preprocessing.py`.**
Descriptive analytics are discussed in further detail in the report. You can run the descriptive analytics code yourself by running:

```bash
./descriptive_analytics.py
```

## PageRank
The PageRank Python script contains a derived version of PageRank which assigns a probability score to significant IP addresses in the dataset. Run it using the below command:

```bash
./pagerank.py
```

## Graph analysis
The Graph Analysis script takes the results of the PageRank script (which determined the most significant IP addresses in the dataset samples) and creates a Graph of that data, which therefore indicates the IP addresses which saw the most traffic. It also performs (true) PageRank in order to assign true significance based on the data subset.

To do this, run:
```bash
spark-submit --packages graphframes:graphframes:0.6.0-spark2.3-s_2.11 graph_analysis.py
```

# Predictive analytics
The Predictive Analytics section comprises the concept of training a model on the dataset in order to classify new incoming data. The first step is to run the feature reduction script which analyses the correlation coefficients of each pair of features within the dataset in order to find the most highly-correlated features.

## Feature selection/reduction
You will need to run the `feature_reduction.py` script to find the highest correlated features. The script will output two matrix plots to `output/features/matrix`, one containing a heatmap of correlation coefficients of all the features, and the other containing a matrix of the 15 most highly-correlated variables.

Launch the script by running:
```bash
./feature_reduction.py
```

## Prediction model
A non-realtime model is created in `prediction_model.py`. This script generates the output containing statistical measures based on the model declared in the file.

This script requires Spark in order to run. The script can be run with the following command:
```bash
spark-submit prediction_model.py
```

From the findings of this model, we can move onto the real-time analytics module.

# Setting up the virtual network
Before running the real-time prediction model, a virtual network must be created to generate the packet flows for it to predict on.

## Installing Docker
The virtual network runs in Docker containers. There are two containers in total. One is for running the Apache web server with a dummy web page and the other is for running the traffic scripts.

More detail is available in the code for each script, and they are located in the `docker/` folder of this repository.

Assuming you are running Ubuntu, you will first need to install Docker by following the instructions at this link: [https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/](https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/)

Then, you need to install Docker Compose by following the instructions here: [https://docs.docker.com/v17.09/compose/install/](https://docs.docker.com/v17.09/compose/install/)

## Launching the containers
Now you can launch the Docker containers. `cd` to the root of this repository and run the following command:

```bash
sudo docker-compose up -d
```

You can verify the containers are up by running:

```bash
sudo docker-compose ps
```

And you should see an output similar to that below:
```
Name                  Command             State   Ports
-------------------------------------------------------------
ddos             python3 ddos.py               Up            
normal_traffic   python3 normal_traffic.py     Up            
slowloris        python3 slowloris.py target   Up            
target           httpd-foreground              Up      80/tcp
```

If the above output is what you see, then the virtual network has been created successfully.

# Acquiring the packet sniffing tool
The packet sniffing tool used for this project is [TCPDUMP_and_CICFlowMeter by Pasakorn Tiwatthanont](https://github.com/iPAS/TCPDUMP_and_CICFlowMeter). *Logged in as your hadoop user*, you should clone the repository to your home folder - e.g. `/home/hduser/` by running the following command:

```bash
cd ~
git clone https://github.com/iPAS/TCPDUMP_and_CICFlowMeter.git
```

The packet sniffer needs to be run as `sudo`. To this end, we need to force a couple of folders to be public so that the resulting `.pcap` files can be written correctly. Run the following commands to give write permission to the `pcap` and `csv` folders. Start by `cd`-ing into the newly-cloned directory. Then run the folliwing:

```bash
chmod 777 pcap
chmod 777 csv
```
