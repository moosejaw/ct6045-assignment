FROM debian:buster

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install python3 python3-pip git libcap2-bin
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tshark
RUN apt-get -y install libcap2-bin

RUN groupadd wireshark
RUN usermod -a -G wireshark root
RUN newgrp wireshark
RUN chgrp wireshark /usr/bin/dumpcap
RUN setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap

CMD ["tshark"]
