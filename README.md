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

And the requirements should be installed for you automatically. You can do this within a virtual environment if you wish, just remember to always run `source venv_folder/bin/activate` whenever you opt to run the code.

## Cloning
Clone this repository into your home folder, logged in as your hadoop user. My hadoop user is `hduser`, so the project is present in `/home/hduser/ct6045-assignment`.

# Preparing the dataset
You should ensure that the .csv files from the GeneratedLabelledFlows folder are present in a `dataset/` folder in the root of this project directory.

First, you need to run `preprocessing.py`. This is a Python script which processes each file in multiple threads. Comments about specific functionality are available in the Python script itself.

You can run the script by ensuring it has execute permissions and running:
```bash
./preprocessing.py
```

You should see a message saying `Done!` if the script has executed successfully.

The newly-processed `.csv` files are located in a folder named `output/` relative to the root of this project directory.

# Descriptive analytics
## PageRank
**You must do this after you have run `preprocessing.py`.**

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

## Splitting the data into training/testing
We must then split the data into separate files containing the training and testing data respectively. To do this, run:

```bash
./train_test_split.py
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

The packet sniffer needs to be run as `sudo`. To this end, we need to force a couple of folders to be public so that the resulting `.pcap` files can be written correctly. Run the following commands to give write permission to the `pcap` and `csv` folders. Start by `cd`-ing into the newly-cloned directory. Then run the following:

```bash
chmod 777 pcap
chmod 777 csv
```

# Constructing the pipeline
Now we can move onto constructing the pipeline to move data from the Docker network interface into the model. Follow this section closely:

## Tab 1: Streaming packets to HDFS
Open a new terminal tab and log into your hduser. `cd` to this directory and run:

```bash
./stream_packets_to_rta.py
```

And follow the instructions on-screen until you see the message `Waiting for .csv files...`.

You can also modify this file to determine how many files you want to be treated as training data.

## Tab 2: Real-time model
Open a new terminal tab and *remain* as your `sudo` user. We need to modify `config/malicious_ips.txt` to reflect IP address of both the `ddos` and `slowloris` containers.

`cd` to this directory and run:

```bash
sudo docker inspect ddos
```

And copy the IP address field near the bottom of the output. You can then load it directly into `config/malicious_ips.txt` by running:

```bash
echo [IP_ADDRESS] > config/malicious_ips.txt
```

Now do the same for `slowloris`, but make sure you *append* the IP address to the `malicious_ips.txt` file and not overwrite it:

```bash
sudo docker inspect slowloris
echo [IP_ADDRESS] >> config/malicious_ips.txt
```

Now, *log into your hduser.* `cd` to this directory and run:

```bash
spark-submit real_time_analytics.py
```

The model will then wait for incoming data to be written to HDFS.

## Tab 3: Running the packet capture
Open a new terminal tab and *remain* as your `sudo` user. Then, run the `ifconfig` command and copy the interface ID representing the Docker bridge. You can usually tell this as it is the interface beginning with `br-`. In my specific case:

```
br-beabce59d29a: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.19.0.1  netmask 255.255.0.0  broadcast 172.19.255.255
        ether 02:42:e9:73:31:39  txqueuelen 0  (Ethernet)
        RX packets 18812  bytes 28529728 (28.5 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 12  bytes 1188 (1.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:1a:1f:e0:c8  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
enp0s3: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.0.2.15  netmask 255.255.255.0  broadcast 10.0.2.255
        inet6 fe80::aadb:f1e8:a4de:845f  prefixlen 64  scopeid 0x20<link>
        ether 08:00:27:e6:2c:c9  txqueuelen 1000  (Ethernet)
        RX packets 28  bytes 6676 (6.6 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 64  bytes 7663 (7.6 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 96  bytes 6698 (6.6 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 96  bytes 6698 (6.6 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
vethd7566c8: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether 2e:d0:01:a1:eb:28  txqueuelen 0  (Ethernet)
        RX packets 4772324  bytes 3736613025 (3.7 GB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 718  bytes 346339 (346.3 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
vethe47f34b: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether ae:c4:c7:ae:b4:9c  txqueuelen 0  (Ethernet)
        RX packets 710  bytes 345613 (345.6 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 4772331  bytes 3736613634 (3.7 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

So the network interface I want to listen on is `br-beabce59d29a`, so this is what I will copy.

Now, we run the packet capture tool. Ensure you are a `sudo` user and `cd` to the TCPDUMP_AND_CICFlowMeter directory, in my case, `/home/hduser/TCPDUMP_and_CICFlowMeter`. The syntax is `capture_interface_pcap.sh [INTERFACE] [LOCATION_TO_SAVE_PCAP_FILES]`:

```bash
./capture_interface_pcap.sh br-beabce59d29a ~
```

Now, every minute, the packets will be converted to `.pcap` files and automatically converted to `.csv` files, which will be detected by tab 2. The script running in tab 2 will automatically move these files onto HDFS and delete them for you.

# Running the Generated Model
To run the high-performing model, you must first run the capture script described in tab 3 and ensured that the `stream_packets_to_rta.py` script is no longer running.

Allow the packet capture to run for several minutes and the `.csv` files to be created. Then, navigate to the `TCPDUMP_AND_CICFlowMeter/csv` directory and `touch` two new files named `a.csv` and `b.csv` respectively.

`a.csv` represents the training data, so append each file you want to use for training data to this file, like so:

```bash
cat file1.csv >> a.csv
cat file2.csv >> a.csv
...
cat filen.csv >> a.csv
```

Repeat the same process for `b.csv` but only for the files you want to be treated as testing data. Now, open a new tab and log into your `hduser`. `cd` to this project directory and run the following commands:

```bash
mkdir -p output/generated/training
mkdir output/generated/testing
```

Move into your other tab (where you ran `cat`) and `mv` each file to the respective destination. As `a.csv` is training data, we move it to `training` like so:


```bash
sudo mv a.csv /home/hduser/output/generated/training
````

And `b.csv` like this:

```bash
sudo mv b.csv /home/hduser/output/generated/testing
```

Then we need to give ownership of the new diectories to `hduser`:

```bash
sudo chown -R hduser:hadoop /home/hduser/output/generated
```

You can then run the generated model by logging back into your `hduser` and running:
```bash
spark-submit generated_prediction_model.py
```
