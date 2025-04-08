
from modules.fetch_data.domain.meli_interface import InterfaceCRUDCommand


class ReadDataOperation(InterfaceCRUDCommand):

	def __init__(self, total_id: list, total_attributes: list):
		self.total_id = total_id
		self.total_attributes = total_attributes

	def operation(self, obj_get_meli_data):

		meli_data = obj_get_meli_data.request()

		total_items_filtered = []
		for name_id in self.total_id:
			
			if len(self.total_attributes) == 0:
				id_register = meli_data[name_id]
				return id_register
			
			if name_id not in meli_data: continue

			item_filter_value = {'name': name_id}
			for name_attribute in self.total_attributes:
				
				if name_attribute not in meli_data[name_id]: continue

				value_attribute = meli_data[name_id][name_attribute]
				item_filter_value[name_attribute] = value_attribute
			total_items_filtered.append(item_filter_value)

		return total_items_filtered