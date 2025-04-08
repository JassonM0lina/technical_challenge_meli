from __future__ import annotations
from modules.fetch_integrate.domain.integration_interface import ContextState
from modules.fetch_integrate.domain.integration_constant import EnvConstant
from modules.fetch_integrate.appication.pipeline_state import StateInitIntegration, StateCheckDocument, StateCompleteInfoItem
from modules.fetch_integrate.infraestructure.integration_connection import FileExtract, UpdateDocumentMongo, RequestExternalResource, FindDocumentMongo


class IntegrationApiFacade:

  def __init__(self, parameter, debug: bool = False):
    self.parameter: dict = parameter
    self.is_debug: str =  '_DEBUG' if debug else ''

  def operation(self):

    env_constat = EnvConstant()
    name_file: str = self.parameter['name_file']
    self.parameter['file_location'] = f'{env_constat.STR_LOCATION_DATA}/{name_file}'
    self.parameter['url_mongo_connection'] = env_constat.__dict__[f'URL_MONGO_CONNECTION{self.is_debug}']
    self.parameter['items_url'] = env_constat.__dict__[f'URL_GET_MELI_API_ITEM{self.is_debug}']
    self.parameter['categories_url'] = env_constat.__dict__[f'URL_GET_MELI_API_CATEGORIES{self.is_debug}']
    self.parameter['currencies_url'] = env_constat.__dict__[f'URL_GET_MELI_API_CURRENCIES{self.is_debug}']
    self.parameter['register_attributes'] = self.parameter.get('register_attributes', ['price', 'name', 'description'])
    self.parameter['len_batch'] = self.parameter.get('len_batch', 50)

    save_info_register = {key: None for key in ['site', 'id', *self.parameter['register_attributes']]}

    iter_file_extract = FileExtract(self.parameter)
    obj_update_mongo =  UpdateDocumentMongo(self.parameter['url_mongo_connection'], 'meli_data')
    obj_find_mongo = FindDocumentMongo(self.parameter['url_mongo_connection'], 'meli_data')
    obj_request_resource = RequestExternalResource()


    state_get_info_item = StateCompleteInfoItem(obj_update_mongo, obj_request_resource, save_info_register)
    state_check_document = StateCheckDocument(obj_find_mongo, state_get_info_item)
    state_init_integration = StateInitIntegration(iter_file_extract, state_check_document)

    context_process = ContextState(self.parameter)
    context_process.transition_to(state_init_integration)
    context_process.request()
    


    
    

