#from modules.integration.domain.manage_state import Context
#from modules.integration.application.pipeline_state import ConcreteStateA
#from modules.mock_meli.infraestructure.mock_facade import MockFacade
#
from modules.fetch_data.infraestructure.meli_facade import MeliApiFacade


#ids = 'MLA750925229,MLA845041373'
#attributes = 'stock,price'
ids = 'CAT275'
attributes = 'name'

list_id = ids.split(',') if ids else []
list_attributes = attributes.split(',') if attributes else []

api_parameter = {
  'name_file': 'meli_categories_data.json',
  'total_id': list_id
}

total_items_filtered = MeliApiFacade(api_parameter).operation()

pass









#mock_facade = MockFacade('MLA750925229', parameter)
#register = mock_facade.operation()
#print(register)

#context = Context(ConcreteStateA(parameter))
#context.request()
