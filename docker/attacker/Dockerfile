FROM python:3.6-slim
WORKDIR /usr/src/app

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install git

RUN git clone https://github.com/gkbrk/slowloris.git

COPY ./scripts/ ./
RUN chmod +x ./normal_traffic.py
RUN chmod +x ./ddos.py
RUN chmod +x ./frontend.py
CMD ["./frontend.py"]
