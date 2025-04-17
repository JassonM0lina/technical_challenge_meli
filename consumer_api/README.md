# Consumer API Microservice

This microservice consumes data from Kafka, processes it using Apache Spark, and stores the results in MongoDB.

## Features

- Kafka consumer using PySpark Structured Streaming
- Real-time data processing with Apache Spark
- MongoDB integration for data storage
- Configurable batch processing
- Environment variable configuration

## Requirements

- Python 3.11
- Apache Spark 3.5.5
- Kafka
- MongoDB

## Configuration

The microservice can be configured using environment variables:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka bootstrap servers (default: kafka:9093)
- `KAFKA_TOPIC`: Kafka topic to consume from (default: meli_products)
- `MONGO_URL`: MongoDB connection URL (default: mongodb://integration-db:27017/)
- `MONGO_DATABASE`: MongoDB database name (default: meli_data)
- `MONGO_COLLECTION`: MongoDB collection name (default: processed_items)
- `CHECKPOINT_LOCATION`: Location for Spark checkpointing (default: /tmp/checkpoint)
- `BATCH_INTERVAL`: Batch processing interval in seconds (default: 5)

## Running the Microservice

### Using Docker

```bash
# Build the Docker image
docker build -t consumer-api .

# Run the container
docker run -d --name consumer-api consumer-api
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Data Flow

1. The microservice consumes JSON messages from a Kafka topic
2. Apache Spark processes the data in batches
3. Processed data is stored in MongoDB

## Schema

The expected schema for Kafka messages:

```json
{
  "site": "string",
  "id": "string",
  "price": "number",
  "name": "string",
  "description": "string"
}
```

## Monitoring

The microservice logs processing information to stdout, including:
- Batch processing statistics
- Sample of processed data
- MongoDB insertion results
- Error messages 