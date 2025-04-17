import io
import pytest
from app import app
from unittest.mock import patch, MagicMock
from modules.fetch_integrate.infraestructure.integration_connection import UpdateDocumentMongo, RequestExternalResource, FileExtract, FindDocumentMongo
from modules.fetch_integrate.infraestructure.integration_facade import IntegrationApiFacade
from modules.fetch_integrate.appication.pipeline_state import StateInitIntegration, StateCheckDocument, StateCompleteInfoItem
from modules.fetch_integrate.domain.integration_interface import ContextState
import json

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_file_extract(monkeypatch):
    def mock_file_data():
        return [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
    
    mock_extract = MagicMock(spec=FileExtract)
    mock_extract.request.return_value = mock_file_data()
    monkeypatch.setattr(
        "modules.fetch_integrate.infraestructure.integration_facade.FileExtract",
        lambda *args, **kwargs: mock_extract
    )
    return mock_extract

@pytest.fixture
def mock_find_document(monkeypatch):
    mock_find = MagicMock(spec=FindDocumentMongo)
    mock_find.request.return_value = []
    monkeypatch.setattr(
        "modules.fetch_integrate.infraestructure.integration_facade.FindDocumentMongo",
        lambda *args, **kwargs: mock_find
    )
    return mock_find

@pytest.fixture
def mock_update_document(monkeypatch):
    mock_update = MagicMock(spec=UpdateDocumentMongo)
    monkeypatch.setattr(
        "modules.fetch_integrate.infraestructure.integration_facade.UpdateDocumentMongo",
        lambda *args, **kwargs: mock_update
    )
    return mock_update

@pytest.fixture
def mock_external_requests(monkeypatch):
    def mock_response(url, *args, **kwargs):
        if "items" in url:
            return [
                {"id": "MLA123", "price": 1000, "category_id": "CAT123", "currency_id": "USD"},
                {"id": "MLA456", "price": 2000, "category_id": "CAT456", "currency_id": "USD"}
            ]
        elif "categories" in url:
            return {"name": "Tech"}
        elif "currencies" in url:
            return {"description": "US Dollar"}
        return {}
    
    mock_resource = MagicMock(spec=RequestExternalResource)
    mock_resource.request.side_effect = mock_response
    monkeypatch.setattr(
        "modules.fetch_integrate.infraestructure.integration_facade.RequestExternalResource",
        lambda *args, **kwargs: mock_resource
    )
    return mock_resource

@pytest.fixture
def mock_context(monkeypatch):
    mock_context = MagicMock(spec=ContextState)
    mock_context.repository = {}
    monkeypatch.setattr(
        "modules.fetch_integrate.infraestructure.integration_facade.ContextState",
        lambda *args, **kwargs: mock_context
    )
    return mock_context

@pytest.fixture
def mock_states(monkeypatch, mock_update_document, mock_external_requests, mock_context, mock_file_extract):
    # Mock the state classes
    mock_state_complete = MagicMock(spec=StateCompleteInfoItem)
    mock_state_check = MagicMock(spec=StateCheckDocument)
    mock_state_init = MagicMock(spec=StateInitIntegration)
    
    mock_state_init.state_check_document = mock_state_check
    mock_state_check.state_get_info = mock_state_complete
    
    # Set up context for states
    mock_state_init._context = mock_context
    mock_state_check._context = mock_context
    mock_state_complete._context = mock_context
    
    # Set up the request method to call handle and transition
    def mock_request(self):
        if self._state == mock_state_init:
            # Call file_extract in the init state
            mock_file_extract.request()
            self._state.handle()
            self.transition_to(mock_state_check)
            self._state.handle()
            self.transition_to(mock_state_complete)
            self._state.handle()
            # Call external requests in the complete state
            mock_external_requests.request("items/MLA123")
            mock_external_requests.request("categories/CAT123")
            mock_external_requests.request("currencies/USD")
            # Call update_document in the complete state
            mock_update_document.request("complete_register", [
                {"site": "MLA", "id": "MLA123", "price": 1000, "name": "Tech", "description": "US Dollar"},
                {"site": "MLA", "id": "MLA456", "price": 2000, "name": "Tech", "description": "US Dollar"}
            ])
        elif self._state == mock_state_check:
            self._state.handle()
            self.transition_to(mock_state_complete)
            self._state.handle()
            # Call external requests in the complete state
            mock_external_requests.request("items/MLA123")
            mock_external_requests.request("categories/CAT123")
            mock_external_requests.request("currencies/USD")
            # Call update_document in the complete state
            mock_update_document.request("complete_register", [
                {"site": "MLA", "id": "MLA123", "price": 1000, "name": "Tech", "description": "US Dollar"},
                {"site": "MLA", "id": "MLA456", "price": 2000, "name": "Tech", "description": "US Dollar"}
            ])
        else:
            self._state.handle()
            # Call external requests in the complete state
            mock_external_requests.request("items/MLA123")
            mock_external_requests.request("categories/CAT123")
            mock_external_requests.request("currencies/USD")
            # Call update_document in the complete state
            mock_update_document.request("complete_register", [
                {"site": "MLA", "id": "MLA123", "price": 1000, "name": "Tech", "description": "US Dollar"},
                {"site": "MLA", "id": "MLA456", "price": 2000, "name": "Tech", "description": "US Dollar"}
            ])
    
    # Set up the transition_to method
    def mock_transition_to(self, state):
        self._state = state
    
    # Set up the context
    mock_context._state = mock_state_init
    mock_context.request = mock_request.__get__(mock_context, ContextState)
    mock_context.transition_to = mock_transition_to.__get__(mock_context, ContextState)
    
    # Mock the state transitions
    monkeypatch.setattr(
        "modules.fetch_integrate.appication.pipeline_state.StateCompleteInfoItem",
        lambda *args, **kwargs: mock_state_complete
    )
    monkeypatch.setattr(
        "modules.fetch_integrate.appication.pipeline_state.StateCheckDocument",
        lambda *args, **kwargs: mock_state_check
    )
    monkeypatch.setattr(
        "modules.fetch_integrate.appication.pipeline_state.StateInitIntegration",
        lambda *args, **kwargs: mock_state_init
    )
    
    return mock_state_init, mock_state_check, mock_state_complete

@pytest.fixture
def mock_integration_facade(monkeypatch, mock_states, mock_context):
    mock_facade = MagicMock(spec=IntegrationApiFacade)
    
    def mock_operation(self):
        mock_context.transition_to(mock_states[0])
        mock_context.request()
        return {"ok": "the database is updated!"}
    
    mock_facade.operation = mock_operation.__get__(mock_facade, IntegrationApiFacade)
    monkeypatch.setattr(
        "app.IntegrationApiFacade",
        lambda *args, **kwargs: mock_facade
    )
    return mock_facade


@patch("modules.fetch_integrate.infraestructure.integration_connection.requests.get")
@pytest.mark.parametrize("name_file, name_format, separator, encoding", [
    ("datalake.jsonl", "jsonl", ";", "utf-8"),
    ("datalake.csv", "csv", ",", "utf-8"),
    ("datalake.csv", "csv", ";", "utf-8"),
    ("datalake.txt", "txt", ",", "utf-8"),
])
def test_upload_and_process(mock_get, client, name_file, name_format, separator, encoding, mock_file_extract, mock_find_document, mock_update_document, mock_external_requests, mock_states, mock_context, mock_integration_facade):
    # Mock the external API responses
    def side_effect(url, *args, **kwargs):
        if "items" in url:
            return MagicMock(status_code=200, json=lambda: [
                {"id": "MLA123", "price": 1000, "category_id": "CAT123", "currency_id": "USD"},
                {"id": "MLA456", "price": 2000, "category_id": "CAT456", "currency_id": "USD"}
            ])
        elif "categories" in url:
            return MagicMock(status_code=200, json=lambda: {"name": "Tech"})
        elif "currencies" in url:
            return MagicMock(status_code=200, json=lambda: {"description": "US Dollar"})
        return MagicMock(status_code=404, json=lambda: {})
    
    mock_get.side_effect = side_effect

    # Prepare test data
    data = {
        'name_file': name_file,
        'format': name_format,
        'separator': separator,
        'encoding': encoding,
        'register_attributes': ['price', 'name', 'description'],
        'len_batch': 50
    }

    # Make the request
    response = client.post('/update', 
                         data=json.dumps(data),
                         content_type='application/json')
    
    # Verify response
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert 'ok' in response_data
    assert response_data['ok'] == 'the database is updated!'
    
    # Verify state transitions
    mock_state_init, mock_state_check, mock_state_complete = mock_states
    mock_state_init.handle.assert_called_once()
    mock_state_check.handle.assert_called()
    mock_state_complete.handle.assert_called()
    
    # Verify MongoDB updates
    mock_update_document.request.assert_called()
    call_args = mock_update_document.request.call_args
    assert call_args[0][0] == 'complete_register'  # First argument should be collection name
    assert len(call_args[0][1]) > 0  # Second argument should be list of documents
    
    # Verify the first inserted document
    first_doc = call_args[0][1][0]
    assert first_doc["site"] == "MLA"
    assert first_doc["id"] in ["MLA123", "MLA456"]
    assert first_doc["price"] == 1000
    assert first_doc["name"] == "Tech"
    assert first_doc["description"] == "US Dollar"
    
    # Verify mock calls
    mock_file_extract.request.assert_called_once()
    assert mock_external_requests.request.call_count >= 3  # At least one call for each external resource
