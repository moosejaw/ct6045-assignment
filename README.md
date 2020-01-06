# Introduction
This repository contains the supplementary code for the CT6045 assignment. Instructions on how to run each piece of code are available in this file. You should read each section of this file in order, as one section may depend on you having run another piece of code from a previous section.

# Installing Python requirements
There are several requirements which this project needs in order to run. You can download them all at once by simply running:

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
You will need to run the `feature_reduction.py` script to do this. The script will output two matrix plots to `output/features/matrix`, one containing a heatmap of correlation coefficients of all the features, and the other containing a matrix of the 15 most highly-correlated variables.

Launch the script by running:
```bash
./feature_reduction.py
```

# Setting up the virtual network
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
Name         Command        State   Ports
--------------------------------------------
attacker   ./frontend.py      Up            
target     httpd-foreground   Up      80/tcp
```

## Monitoring traffic flows
The traffic is monitored through `tshark`. You first need to install it by running:

```bash
sudo apt-get install tshark
```

You then need to add your user to the `wireshark` group. As my user is called `josh`, I do this like below:

```bash
sudo usermod -a -G wireshark josh
```

**You must restart your terminal emulator for these changes to take effect, otherwise you will not be able to run `tshark`.**

You then need to find the network interface which `docker-compose` is communicating on. Docker Compose uses a bridge network interface for inter-container traffic. You can locate it by running:

```bash
ifconfig
```

And selecting the result with the `br-` prefix. For example, my `ifconfig` output is as below:

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

So the network interface I want to listen on is `br-beabce59d29a`. I can check this is correct by running:

```bash
tshark -i br-beabce59d29a
```

You should see a constant stream of packets being transmitted with length `1490` (as defined in `ddos.py`). This is how you can tell if you are listening on the correct interface.
