
from modules.fetch_integrate.infraestructure.integration_facade import IntegrationApiFacade

parameter ={
  #'register_attributes': ['price', 'name', 'description'],
  'len_batch': 50,
  'name_file': 'datalake.csv',
  'format': 'csv',
  'separator': ',',
  'encoding': 'utf-8',
}

#try:
IntegrationApiFacade(parameter, debug = True).operation()
#	response = {'ok':'the database is updated!'}
#except Exception as e:
#	response = {'error': str(e)}
	
pass
