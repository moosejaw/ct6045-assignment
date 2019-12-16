FROM python:3.6-slim
WORKDIR /usr/src/app

RUN apt-get update && apt-get upgrade
RUN apt-get install git

RUN git clone https://github.com/gkbrk/slowloris.git

COPY ./scripts/ ./
RUN chmod +x ./normal_traffic.py
RUN chmod +x ./ddos.py
CMD ["./frontend.py"]
