# Use official OpenJDK 17 with Python 3.9 base image
FROM openjdk:17-slim

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean

# Set environment variables for Java
ENV JAVA_HOME=/usr/local/openjdk-17
ENV PATH=$JAVA_HOME/bin:$PATH

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY app.py .
COPY randomforest_pipeline_model ./randomforest_pipeline_model

EXPOSE 5000

CMD ["python3", "app.py"]

