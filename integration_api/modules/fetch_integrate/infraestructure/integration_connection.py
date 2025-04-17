from modules.fetch_integrate.domain.integration_interface import InterfaceConnection
from confluent_kafka import Producer
from pymongo import MongoClient
import requests
import json
import csv
import os


class FileExtract(InterfaceConnection):

  def __init__(self, parameter: dict):
    self.file_location: str = parameter['file_location']
    self.file_format: str = parameter['format']
    self.encoding: str = parameter['encoding']
    self.separator: str = parameter['separator']
    
  def request(self):
    with open(self.file_location, mode="r", encoding=self.encoding) as f:
      if self.file_format in ["csv","txt"]:
        reader = csv.DictReader(f, delimiter=self.separator)
        for row in reader:
          yield row

      elif self.file_format == "jsonl":
        for line in f:
          if line.strip():
            yield json.loads(line)
      else:
          raise ValueError(f"Unsupported format: {self.file_format}")

class FindDocumentMongo(InterfaceConnection):

  def __init__(self, url_mongo_connection: str, name_database: str):
    self.url_connection = url_mongo_connection
    self.name_database = name_database
  
  def request(self, name_collection: dict, query: dict, attributes: dict):
    
    client = MongoClient(self.url_connection)
    db = client[self.name_database]
    collection = db[name_collection]
    return collection.find(query, attributes)

class UpdateDocumentMongo(InterfaceConnection):

  def __init__(self, url_mongo_connection: str, name_database: str):
    self.url_connection = url_mongo_connection
    self.name_database = name_database
  
  def request(self, name_collection: dict, register: list):
    
    client = MongoClient(self.url_connection)
    db = client[self.name_database]
    collection = db[name_collection]
    collection.insert_many(register)

class RequestExternalResource(InterfaceConnection):

	def request(self, url_request: str, params: dict, total_attributes: list = []):
		try:
			response = requests.get(url_request, params=params)
			
			if response.status_code != 200:
				raise Exception(f"HTTP error occurred: {response.status_code}")
				
			response_data = response.json()
			
			if len(total_attributes) == 0:
				return response_data
			return {key: value for key, value in response_data.items() if key in total_attributes}
			
		except requests.exceptions.ConnectionError as e:
			raise ConnectionError(f"Connection failed: {str(e)}")
		except json.JSONDecodeError as e:
			raise ValueError(f"Invalid JSON response: {str(e)}")
		except Exception as e:
			raise Exception(f"Error occurred: {str(e)}")
			
class KafkaConnection:
    def __init__(self, kafka_bootstrap_servers, kafka_topic):
        self.producer = Producer({
            'bootstrap.servers': kafka_bootstrap_servers,
            'client.id': 'integration_api_producer'
        })
        self.topic = kafka_topic

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def publish_message(self, message):
        try:
            # Convert message to JSON string
            message_str = json.dumps(message)
            
            # Produce message to Kafka
            self.producer.produce(
                topic=self.topic,
                value=message_str.encode('utf-8'),
                callback=self.delivery_report
            )
            
            # Wait for all messages to be delivered
            self.producer.flush()
            
            return True
        except Exception as e:
            print(f"Error publishing message to Kafka: {str(e)}")
            return False 

