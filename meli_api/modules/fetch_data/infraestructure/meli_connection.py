from modules.fetch_data.domain.meli_interface import InterfaceConnection
import json
import os


class FileExtract(InterfaceConnection):

  def __init__(self, location_file: str):
    self.location_file = location_file
    
  def request(self):

    with open(self.location_file, "r", encoding="utf-8") as file:
      data = json.load(file)
      return data