FROM python:3.6-slim
WORKDIR /usr/src/app

COPY ./scripts/ ./
RUN chmod +x ./normal_traffic.py
CMD ["./normal_traffic.py"]
