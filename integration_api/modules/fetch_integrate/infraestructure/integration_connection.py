from modules.fetch_integrate.domain.integration_interface import InterfaceConnection
from pymongo import MongoClient
import requests
import json
import csv


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
		
		response_data = {key: None for key in total_attributes}
		response = requests.get(url_request, params=params)
		
		if response.status_code == 200:	
			response_data = response.json() 
			if len(total_attributes) == 0:
				return response_data
			return {key: value for key, value in response_data.items() if key in total_attributes}
		
		return response_data
			





