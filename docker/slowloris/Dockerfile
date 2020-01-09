FROM python:3.6-slim
WORKDIR /usr/src/app

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install git

RUN git clone https://github.com/gkbrk/slowloris.git

WORKDIR /usr/src/app/slowloris
CMD ["python3", "slowloris.py"]
