
from modules.fetch_integrate.infraestructure.integration_facade import IntegrationApiFacade, IntegrationAPIVersion2

parameter ={
  #'register_attributes': ['price', 'name', 'description'],
  "register_attributes": ["price", "name", "description"],
  "len_batch": 50,
  "name_file": "datalake.jsonl",
  "format": "jsonl",
  "separator": ",",
  "encoding": "utf-8"
}

#try:
IntegrationAPIVersion2(parameter, debug = True).operation()
#	response = {'ok':'the database is updated!'}
#except Exception as e:
#	response = {'error': str(e)}
	
pass
