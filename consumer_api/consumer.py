from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from pyspark.sql import Row
import requests
import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import List, Dict, Generator

# ---------------------- Logging Configuration ---------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Load Environment Variables ---------------------- #
load_dotenv()

# ---------------------- Kafka and Mongo Configuration ---------------------- #
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9093")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "meli_products")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "meli_data")
COLLECTION_COMPLETE = os.getenv("COLLECTION_COMPLETE", "complete_register")
COLLECTION_INCOMPLETE = os.getenv("COLLECTION_INCOMPLETE", "incomplete_register")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))

#client = MongoClient(MONGO_URI)
#db = client[MONGO_DATABASE]
#collection_complete = db[COLLECTION_COMPLETE]
#collection_incomplete = db[COLLECTION_INCOMPLETE]

# ---------------------- Kafka Schema Definition ---------------------- #
schema = StructType([
    StructField("register_attributes", ArrayType(StringType()), True),
    StructField("len_batch", StringType(), True),
    StructField("name_file", StringType(), True),
    StructField("format", StringType(), True),
    StructField("separator", StringType(), True),
    StructField("encoding", StringType(), True),
    StructField("file_location", StringType(), True)
])

# ---------------------- Kafka Topic Creation ---------------------- #
def create_kafka_topic():
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            client_id="topic-init"
        )
        topic = NewTopic(name=KAFKA_TOPIC, num_partitions=3, replication_factor=1)
        admin_client.create_topics(new_topics=[topic], validate_only=False)
        logger.info(f"Kafka topic '{KAFKA_TOPIC}' created successfully.")
    except TopicAlreadyExistsError:
        logger.info(f"Kafka topic '{KAFKA_TOPIC}' already exists.")
    except Exception as e:
        logger.error(f"Failed to create Kafka topic: {e}")
    finally:
        admin_client.close()

# ---------------------- Spark Session Creation ---------------------- #
def create_spark_session():
    logger.info("Creating Spark session...")
    return SparkSession.builder \
        .appName("MeliDataProcessor") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.default.parallelism", "2") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.sql.execution.arrow.pyspark.fallback.enabled", "true") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5") \
        .getOrCreate()

# ---------------------- Load Input File ---------------------- #
def load_input_file(spark, parameter: dict):
    try:
        file_format = parameter.get('format', '').lower()
        name_file = parameter.get('name_file', 'datalake.jsonl')
        separator = parameter.get('separator', ',')
        encoding = parameter.get('encoding', 'utf-8')
        folder_location = os.path.join(os.path.dirname(__file__), 'assets')
        file_location = f'{folder_location}/{name_file}'

        logger.info(f"Loading file: {file_location} with format: {file_format}")

        if file_format == 'csv':
            return spark.read.csv(file_location, sep=separator, encoding=encoding, header=True)
        elif file_format == 'jsonl':
            return spark.read.json(file_location, encoding=encoding)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    except Exception as e:
        logger.error(f"Error loading file: {str(e)}")
        raise

# ---------------------- Process Partition ---------------------- #
def process_partition(rows: List[Row]) -> Generator[Row, None, None]:
    def http_request(url_request: str, params: dict, total_attributes: List[str] = []):
        try:
            response = requests.get(url_request, params=params)
            response.raise_for_status()
            data = response.json()
            return {key: value for key, value in data.items() if key in total_attributes} if total_attributes else data
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def process_batch(batch_register: Dict[str, dict]):
        return http_request('http://meli-api:5000/items', {
            'ids': ','.join(batch_register.keys()),
            'attributes': 'price,category_id,currency_id'
        })

    def enrich_registers(item_info_list, batch_register):
        complete_records = []
        incomplete_records = []
        category_cache, currency_cache = {}, {}

        for item in item_info_list:
            item_id = item['name']
            original = batch_register.get(item_id, {})
            enriched = {
                'site': original.get('site'),
                'id': original.get('id'),
                'price': item.get('price'),
                'name': None,
                'description': None
            }
            cat_id, cur_id = item.get('category_id'), item.get('currency_id')

            if cat_id not in category_cache:
                category_cache[cat_id] = http_request('http://meli-api:5000/categories', {'ids': cat_id}, ['name'])
            if cur_id not in currency_cache:
                currency_cache[cur_id] = http_request('http://meli-api:5000/currencies', {'ids': cur_id}, ['description'])

            enriched['name'] = category_cache[cat_id].get('name')
            enriched['description'] = currency_cache[cur_id].get('description')

            if None in enriched.values():
                incomplete_records.append(enriched)
            else:
                complete_records.append(enriched)

        return complete_records, incomplete_records

    batch_register = {}
    for register in rows:
        register_dict = {}
        for field in register.__fields__:
            register_dict[field] = getattr(register, field)
            
        key = f"{register_dict['site']}{register_dict['id']}"
        batch_register[key] = register_dict

        if len(batch_register) >= BATCH_SIZE:
            logger.info(f"Processing batch of {len(batch_register)} elements.")
            items = process_batch(batch_register)
            complete_records, incomplete_records = enrich_registers(items, batch_register)
            yield Row(complete=complete_records, incomplete=incomplete_records, count=len(complete_records) + len(incomplete_records))
            batch_register = {}

    if batch_register:
        logger.info(f"Processing final batch of {len(batch_register)} elements.")
        items = process_batch(batch_register)
        complete_records, incomplete_records = enrich_registers(items, batch_register)
        yield Row(complete=complete_records, incomplete=incomplete_records, count=len(complete_records) + len(incomplete_records))

# ---------------------- Process Stream ---------------------- #
def process_stream():
    spark = create_spark_session()

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .option("maxOffsetsPerTrigger", "10000") \
        .load()

    logger.info("Successfully created Kafka DataFrame configuration")

    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    def process_batch(batch_df, batch_id):
        rows = batch_df.collect()
        for row in rows:
            try:
                logger.info(f"Processing batch ID {batch_id} with parameters: {row}")
                parameter = row.asDict()
                file_df = load_input_file(spark, parameter)
                logger.info("File loaded successfully.")
                
                # Procesar los datos y obtener los resultados
                results = file_df.rdd.mapPartitions(process_partition).collect()
                
                # Create DataFrames from the collected results
                all_complete_records = [record for r in results for record in r.complete]
                all_incomplete_records = [record for r in results for record in r.incomplete]
                
                # Define schema for the DataFrames
                schema = StructType([
                    StructField("site", StringType(), True),
                    StructField("id", StringType(), True),
                    StructField("price", StringType(), True),
                    StructField("name", StringType(), True),
                    StructField("description", StringType(), True)
                ])
                
                # Create DataFrames with schema, handling empty lists
                complete_df = spark.createDataFrame(all_complete_records, schema) if all_complete_records else spark.createDataFrame([], schema)
                incomplete_df = spark.createDataFrame(all_incomplete_records, schema) if all_incomplete_records else spark.createDataFrame([], schema)
                
                # Process complete documents in batches using Spark
                if not complete_df.rdd.isEmpty():
                    complete_df.foreachPartition(lambda partition: process_partition_to_mongo(
                        partition, COLLECTION_COMPLETE, "complete"
                    ))
                
                if not incomplete_df.rdd.isEmpty():
                    incomplete_df.foreachPartition(lambda partition: process_partition_to_mongo(
                        partition, COLLECTION_INCOMPLETE, "incomplete"
                    ))
                
                logger.info(f"File Upload To Database successfully. Complete records: {complete_df.count()}, Incomplete records: {incomplete_df.count()}")
                
            except Exception as e:
                logger.error(f"Error processing batch ID {batch_id}: {str(e)}")
                raise  # Re-lanzar la excepción para que Spark sepa que hubo un error

    query = parsed_df.writeStream \
        .outputMode("append") \
        .option("checkpointLocation", "/app/checkpoint") \
        .foreachBatch(process_batch) \
        .start()

    query.awaitTermination()

def process_partition_to_mongo(partition, collection_name, doc_type):
    # Create MongoDB connection inside the worker
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DATABASE]
    collection = db[collection_name]
    
    batch = []
    batch_size = 100
    
    try:
        for record in partition:
            batch.append(record.asDict())
            if len(batch) >= batch_size:
                collection.insert_many(batch)
                logger.info(f"Inserted batch of {len(batch)} {doc_type} documents")
                batch = []
        
        # Insert remaining documents
        if batch:
            collection.insert_many(batch)
            logger.info(f"Inserted final batch of {len(batch)} {doc_type} documents")
    except Exception as e:
        logger.error(f"Error processing {doc_type} documents: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    create_kafka_topic()
    process_stream()
