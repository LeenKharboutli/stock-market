# Real-time Data Pipeline

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

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/LeenKharboutli/stock-market-data-pipeline.git
   cd real-time-user-data-pipeline
   ```

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

1. Ensure all services are up and running using `docker compose ps`.
2. Access the Airflow web interface and enable the `user_automation` DAG.
3. Monitor the Kafka Control Center to ensure messages are being produced.
4. Check the Spark UI to see the streaming job in action.
5. Use a Cassandra client to verify that data is being written to the `created_users` table.

## Troubleshooting

- If services fail to start, check the logs using `docker compose logs [service_name]`.
- Ensure all required ports are free on your host machine.
- Verify that the Kafka topics are created correctly.

## Future Improvements

- Replace temporary Random User API with real-world stock market data
- Adjust pipeline scripts to properly handle stock market data
- Add data quality checks
- Implement error handling and retry mechanisms
- Create dashboards for monitoring the pipeline
