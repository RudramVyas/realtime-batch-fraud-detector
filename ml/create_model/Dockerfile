FROM openjdk:8-jre-slim-buster

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pyspark==3.2.1
RUN pip3 install findspark
RUN pip3 install numpy

WORKDIR /app

COPY train_rf_from_hive.py .

CMD ["spark-submit", "--master", "local[*]", "train_rf_from_hive.py"]
