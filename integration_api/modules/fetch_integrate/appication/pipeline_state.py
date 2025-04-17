from modules.fetch_integrate.domain.integration_interface import InterfaceState, InterfaceConnection
import copy

class StateInitIntegration(InterfaceState):

	def __init__(self, iter_file, state_check_document):
		self.iter_file: InterfaceConnection = iter_file
		self.state_check_document: InterfaceState = state_check_document

	def handle(self) -> None:
		
		len_batch_register = self.context.repository['len_batch']

		batch_register = {}
		for register in self.iter_file.request():

			site_item = register['site']
			id_item = register['id']

			batch_register[f'{site_item}{id_item}'] = register
			
			if len(batch_register) >= len_batch_register:

				self.context.transition_to(self.state_check_document)
				self.context.request(batch_register)
				batch_register = {}
		
		if len(batch_register) > 0:
			self.context.transition_to(self.state_check_document)
			self.context.request(batch_register)
		pass		

class StateCheckDocument(InterfaceState):

	def __init__(self, find_document, state_get_info):
		self.check_document: InterfaceConnection = find_document
		self.state_get_info: InterfaceState = state_get_info

	def handle(self, batch_register: dict):

		check_query = {"$or": [{"site": pair["site"], "id": pair["id"]} for pair in batch_register.values()]}
		get_attributes = {"site": 1, "id": 1, "_id": 0}
		result_document = self.check_document.request('complete_register', check_query, get_attributes)

		found_pairs = {f'{doc["site"]}{doc["id"]}' for doc in result_document}
		input_pairs = {*batch_register.keys()}
		
		missing_pairs = input_pairs - found_pairs
		total_items = {key: value for key, value in batch_register.items() if key in missing_pairs}
		print('needed to insert', len(total_items))
		if len(total_items) > 0:
			self.context.transition_to(self.state_get_info)
			self.context.request(total_items)


class StateCompleteInfoItem(InterfaceState):

	def __init__(self, update_database, request_resource, save_info_register):
		self.update_database: InterfaceConnection = update_database
		self.request_resource: InterfaceConnection = request_resource
		self.save_info_register: dict = save_info_register
		
	def handle(self, total_item: dict) -> None:
		
		copy_total_item = copy.deepcopy(total_item)
		base_url_item = self.context.repository['items_url']
		base_url_categories =  self.context.repository['categories_url']
		base_url_currencies = self.context.repository['currencies_url']
		
		item_params = {
			'ids': (',').join(total_item.keys()),
			'attributes': 'price,category_id,currency_id'
		}
		
		list_item_info = self.request_resource.request(base_url_item, item_params)
    
		total_complete_register = []
		total_incomplete_register = []
		for item_register in list_item_info:
			
			copy_total_item.pop(item_register['name'])
			save_register = copy.deepcopy(self.save_info_register)

			save_register['site'] = total_item[item_register['name']]['site']
			save_register['id'] = total_item[item_register['name']]['id']
			
			category_params = {'ids': item_register['category_id']}
			name_category = self.request_resource.request(base_url_categories, category_params, ['name'])
			
			currency_params = {'ids': item_register['currency_id']}
			name_currency = self.request_resource.request(base_url_currencies, currency_params, ['description'])
			
			if 'price' in save_register:
				save_register['price'] = item_register['price']

			if 'name' in save_register:
				save_register['name'] = name_category['name']

			if 'description' in save_register: 
				save_register['description'] = name_currency['description']

			if any(value is None for value in save_register.values()):
				total_incomplete_register.append(save_register)
			else:
				total_complete_register.append(save_register)
		
		print('send complete', len(total_complete_register))
		if len(total_complete_register) > 0:
			self.update_database.request('complete_register', total_complete_register)

		for incomplete_item in copy_total_item.values():
			save_register = copy.deepcopy(self.save_info_register)
			save_register['site'] = incomplete_item['site']
			save_register['id'] = incomplete_item['id']
			total_incomplete_register.append(save_register)

		print('send incomplete', len(total_incomplete_register))
		if len(total_incomplete_register) > 0:
			self.update_database.request('incomplete_register', total_incomplete_register)
