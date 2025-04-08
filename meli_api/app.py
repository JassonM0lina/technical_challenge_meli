from modules.fetch_data.infraestructure.meli_facade import MeliApiFacade

from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/items', methods=['GET'])
def get_items():
	ids = request.args.get('ids', '')
	attributes = request.args.get('attributes', '')

	list_id = ids.split(',') if ids else []
	list_attributes = attributes.split(',') if attributes else []

	api_parameter = {
		'name_file': 'meli_items_data.json',
		'total_id': list_id,
		'total_attributes': list_attributes
	}

	total_items_filtered = MeliApiFacade(api_parameter).operation()
	response = json.dumps(total_items_filtered)

	return app.response_class(response, status=200, mimetype='application/json')

@app.route('/categories', methods=['GET'])
def get_categories():
	name_id = request.args.get('ids', '')

	api_parameter = {
		'name_file': 'meli_categories_data.json',
		'total_id': [name_id]
	}

	total_items_filtered = MeliApiFacade(api_parameter).operation()
	response = json.dumps(total_items_filtered)

	return app.response_class(response, status=200, mimetype='application/json')

@app.route('/currencies', methods=['GET'])
def get_currencies():
	name_id = request.args.get('ids', '')

	api_parameter = {
		'name_file': 'meli_currencies_data.json',
		'total_id': [name_id]
	}

	total_items_filtered = MeliApiFacade(api_parameter).operation()
	response = json.dumps(total_items_filtered)

	return app.response_class(response, status=200, mimetype='application/json')