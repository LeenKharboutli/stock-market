# Real-time Stock Market Data Pipeline

![Data Pipeline Architecture](./data_pipeline_architecture.svg)

## Project Overview

This project implements a robust, scalable data pipeline for processing and analyzing stock market data in real-time. It demonstrates the use of modern data engineering technologies and best practices. This project is a work in progress (WIP). 

## Architecture

The pipeline consists of the following components:

1. **Data Ingestion**: Apache Airflow fetches data from a Random User API (for now) and streams it to Kafka.
2. **Message Queuing**: Apache Kafka handles reliable, high-throughput message queuing.
3. **Data Processing**: Apache Spark processes and transforms the data in real-time.
4. **Data Storage**: Apache Cassandra stores the processed data.
5. **Containerization**: Docker and Docker Compose create a reproducible and scalable environment for the full pipeline.

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Recommended: Unix based system (e.g. MacOS, Linux), as getting Cassandra working is more challenging on Windows

## Versions
This project uses: 

- Spark version 3.5.3
- Scala version 2.12.18 
- OpenJDK 64-Bit Server VM, 17.0.12
- cqlsh 6.2.0
- Cassandra 5.0.1
- CQL spec 3.4.7
- Native protocol v5

To check your Spark, Scala and Open JDK versions, open a terminal and run the following (after running `docker compose up -d` and ensuring all containers are working): 
1. `docker exec -it stock-market-data-pipeline-spark-master-1 sh` (replace `stock-market-data-pipeline-spark-master-1` with the name of the equivalent container running on your system, if the name is different)

2. `spark-submit --version`

To check your cqlsh, Cassandra, CQL, and Native protocol versions, open a terminal and run the following (after running `docker compose up -d` and ensuring all containers are working):

1. `docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042` 

2. `show VERSION`

The versions above are dependent on the images pulled as part of the docker-compose.yml, which is configured to pull the latest image version:

- `bitnami/spark:latest`
- `cassandra:latest`


## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/LeenKharboutli/stock-market-data-pipeline.git
   cd stock-market-data-pipeline
   ```

2. Create a venv while in the project directory (`stock-market-data-pipeline`)
   ```
   python -m venv venv
   ```

3. Download the required jars into `stock-market-data-pipeline/venv/lib/python3.9/site-packages/pyspark/jars/` (the names listed below are formatted to match the requirements listed in spark_stream.py):
   
   - [com.datastax.spark:spark-cassandra-connector_2.12:3.5.1](https://mvnrepository.com/artifact/com.datastax.spark/spark-cassandra-connector_2.12/3.5.1)
   
   - [org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3](https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.12/3.5.3)
   
   - [org.apache.kafka:kafka-clients:3.4.1](https://mvnrepository.com/artifact/org.apache.kafka/kafka-clients/3.4.1)
   
   - [com.datastax.spark:spark-cassandra-connector-assembly_2.12:3.4.1](https://mvnrepository.com/artifact/com.datastax.spark/spark-cassandra-connector-assembly_2.12/3.4.1)
   
   - [org.apache.cassandra:java-driver-core:4.18.1](https://mvnrepository.com/artifact/org.apache.cassandra/java-driver-core/4.18.1)
   
   - [com.typesafe:config:1.4.2](https://mvnrepository.com/artifact/com.typesafe/config/1.4.2)
   
   - [org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.3](https://mvnrepository.com/artifact/org.apache.spark/spark-streaming-kafka-0-10_2.12/3.5.3)
   
   - [org.apache.kafka:kafka_2.12:3.4.1](https://mvnrepository.com/artifact/org.apache.kafka/kafka_2.12/3.4.1)
   
   - [org.apache.commons:commons-pool2:2.11.1](https://mvnrepository.com/artifact/org.apache.commons/commons-pool2/2.11.1)
   
   - [org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.5.3](https://mvnrepository.com/artifact/org.apache.spark/spark-token-provider-kafka-0-10_2.12/3.5.3)

   Alternatively, copy the jars directly from the `required-jars` directory, which has been added to this repository for your convenience.  

2. Build and start the Docker containers:
   ```
   docker compose up -d
   ```

3. Access the various components:
   - Airflow webserver: http://localhost:8080
   - Kafka Control Center: http://localhost:9021
   - Spark Master UI: http://localhost:9090

## Project Structure

- `dags/`: Contains Airflow DAG definitions
- `script/`: Contains entrypoint script
- `spark_stream.py`: Sets up Spark streaming job
- `docker-compose.yml`: Defines and configures the Docker services
- `requirements.txt`: Lists Python dependencies

## Key Components

### Apache Airflow

The `kafka_stream.py` DAG fetches data from the Random User API and sends it to Kafka.

### Apache Kafka

Kafka brokers handle the streaming data. Topics can be managed through the Control Center UI.

### Apache Spark

The `spark_stream.py` script defines a Spark streaming job that processes data from Kafka and writes it to Cassandra.

### Apache Cassandra

Cassandra stores the processed user data in the `spark_streams.created_users` table.

## Usage

1. Ensure all services are up and running using `docker compose ps`. Alternatively, it's recommended to use Docker Desktop to check the status of your containers. 
2. Access the Airflow web interface and enable the `user_automation` DAG.

   a. To access the Airflow web interface, go to `http://localhost:8080` and enter "admin" for both username and password
   
   b. Click on `user_automation` to view the grid

   c. Click on the "play" arrow on the UI to trigger the DAG

3. Monitor the Kafka Control Center to ensure messages are being produced.
4. There are two ways to get Spark streaming going:
   
   a. On a local terminal, run `spark-submit --master spark://localhost:7077 spark_stream.py`
   
   b. In a local terminal open in the `stock-market-data-pipeline` directory, run `python spark_stream.py` 
5. Check the Spark UI to see the streaming job in action.
   
   a. Note: When you submit the Spark job, you can simultaneously trigger the DAG
5. Use a Cassandra client to verify that data is being written to the `created_users` table.

   a. To enter the Cassandra shell, open a new terminal and run `docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042`
   
   b. Run `describe spark_streams.created_users` to get some information on the table

   c. Check the number of records streamed to Cassandra:

      ```
      USE spark_streams;
      SELECT COUNT(*) FROM created_users;
      ```

## Troubleshooting

- Cassandra may throw errors if run on Windows
- If you're running into issues while running spark_stream.py, it may be useful to periodically clear cache: `rm -rf <path-to-.ivy2>/.ivy2/cache`
- If you make changes to the table schema in spark_stream.py, it may be best to restart the containers with `docker compose down; docker compose up -d`
- If services fail to start, check the logs using `docker compose logs [service_name]`.
- Ensure all required ports are free on your host machine.
- Verify that the Kafka topics are created correctly

## Future Improvements

- Replace temporary Random User API with real-world stock market data
- Adjust pipeline scripts to properly handle stock market data
- Add data quality checks
- Implement error handling and retry mechanisms
- Create dashboards for monitoring the pipeline
