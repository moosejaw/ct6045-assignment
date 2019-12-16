# Setting up the virtual network
The virtual network runs in Docker containers. There are two containers in total. One is for running the Apache web server with a dummy web page and the other is for running the traffic scripts.

More detail is available in the code for each script, and they are located in the `docker/` folder of this repository.

Assuming you are running Ubuntu, you will first need to install Docker by following the instructions at this link: [https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/](https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/)

Then, you need to install Docker Compose by following the instructions here: [https://docs.docker.com/v17.09/compose/install/](https://docs.docker.com/v17.09/compose/install/)

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
