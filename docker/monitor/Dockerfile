FROM debian:buster

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install python3 python3-pip git tshark

CMD ["tshark"]
