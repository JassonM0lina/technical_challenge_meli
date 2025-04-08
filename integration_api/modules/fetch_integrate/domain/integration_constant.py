from dataclasses import dataclass
import os

@dataclass(frozen=True)
class EnvConstant:
    
  STR_LOCATION_DATA: str = os.path.join(os.path.dirname(__file__), 'assets')
  
  URL_GET_MELI_API_ITEM_DEBUG: str ='http://localhost:5000/items'
  URL_GET_MELI_API_CATEGORIES_DEBUG: str ='http://localhost:5000/categories'
  URL_GET_MELI_API_CURRENCIES_DEBUG: str ='http://localhost:5000/currencies'
  URL_MONGO_CONNECTION_DEBUG: str = 'mongodb://localhost:27017/'
  
  URL_GET_MELI_API_ITEM: str ='http://meli_api:5000/items'
  URL_GET_MELI_API_CATEGORIES: str ='http://meli_api:5000/categories'
  URL_GET_MELI_API_CURRENCIES: str ='http://meli_api:5000/currencies'
  URL_MONGO_CONNECTION: str = 'mongodb://integration_db:27017/'