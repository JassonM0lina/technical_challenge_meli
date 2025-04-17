from modules.fetch_integrate.infraestructure.integration_facade import IntegrationApiFacade, IntegrationAPIKafka
from flask import Flask, request
import json


app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update_database():
	try:
		parameter = request.get_json()
		IntegrationApiFacade(parameter).operation()
		response = {'ok':'the database is updated!'}
		return app.response_class(json.dumps(response),  status=200, mimetype='application/json')
	except Exception as e:
		response = {'error': str(e)}
		return app.response_class(json.dumps(response),  status=500, mimetype='application/json')


@app.route('/integration', methods=['POST'])
def update_database_get():
	try:
		parameter = request.get_json()
		IntegrationAPIKafka(parameter).operation()
		response = {'ok':'the database is updated!'}
		return app.response_class(json.dumps(response),  status=200, mimetype='application/json')
	except Exception as e:
		response = {'error': str(e)}
		return app.response_class(json.dumps(response),  status=500, mimetype='application/json')

	

