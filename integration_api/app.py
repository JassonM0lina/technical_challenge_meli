from modules.fetch_integrate.infraestructure.integration_facade import IntegrationApiFacade
from flask import Flask, request
import json


app = Flask(__name__)

@app.route('/update', methods=['POST'])
def update_database():
	try:
		parameter = request.get_json()
		IntegrationApiFacade(parameter).operation()
		response = {'ok':'the database is updated!'}
	except Exception as e:
		response = {'error': str(e)}

	return app.response_class(json.dumps(response),  status=200, mimetype='application/json')
