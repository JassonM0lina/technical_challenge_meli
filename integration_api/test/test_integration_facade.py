import pytest
from unittest.mock import patch, MagicMock
from modules.fetch_integrate.infraestructure.integration_facade import IntegrationApiFacade
from modules.fetch_integrate.domain.integration_interface import ContextState

@pytest.fixture
def mock_context():
    # Create a mock parameter dictionary with required fields
    parameter = {
        "name_file": "test_file.txt",
        "format": "csv",
        "encoding": "utf-8",
        "separator": ","
    }
    context = ContextState(parameter)
    return context

@pytest.fixture
def mock_file_extract():
    with patch('modules.fetch_integrate.infraestructure.integration_connection.FileExtract') as mock:
        mock.return_value.request.return_value = [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
        yield mock

@pytest.fixture
def mock_find_document():
    with patch('modules.fetch_integrate.infraestructure.integration_connection.FindDocumentMongo') as mock:
        yield mock

@pytest.fixture
def mock_external_api():
    with patch('modules.fetch_integrate.infraestructure.integration_connection.RequestExternalResource') as mock:
        yield mock

@pytest.fixture
def mock_update_document():
    with patch('modules.fetch_integrate.infraestructure.integration_connection.UpdateDocumentMongo') as mock:
        yield mock

def test_integration_facade_success_flow(
    mock_context,
    mock_file_extract,
    mock_find_document,
    mock_external_api,
    mock_update_document
):
    # Setup mocks
    mock_find_document.return_value.request.return_value = None  # Document not found
    mock_external_api.return_value.request.side_effect = [
        {  # First call - item details
            "id": "MLA123",
            "title": "Test Item",
            "price": 100.0,
            "currency_id": "ARS"
        },
        {  # Second call - currency details
            "id": "ARS",
            "symbol": "$",
            "description": "Peso argentino"
        }
    ]
    mock_update_document.return_value.request.return_value = True

    # Create facade with required parameter
    parameter = {
        "name_file": "test_file",
        "format": "jsonl",
        "encoding": "utf-8",
        "separator": ","
    }
    facade = IntegrationApiFacade(parameter)
    facade.set_context(mock_context)

    # Test operation
    result = facade.operation()

    # Verify
    assert result == {"status": "completed", "ok": True}
    mock_file_extract.return_value.request.assert_called_once()
    mock_find_document.return_value.request.assert_called_once()
    assert mock_external_api.return_value.request.call_count == 2
    mock_update_document.return_value.request.assert_called_once()

def test_integration_facade_document_exists(
    mock_context,
    mock_file_extract,
    mock_find_document,
    mock_external_api,
    mock_update_document
):
    # Setup mocks
    mock_find_document.return_value.request.return_value = {
        "id": "MLA123",
        "site": "MLA",
        "price": 100.0
    }  # Document exists

    # Create facade with required parameter
    parameter = {
        "name_file": "test_file",
        "format": "jsonl",
        "encoding": "utf-8",
        "separator": ","
    }
    facade = IntegrationApiFacade(parameter)
    facade.set_context(mock_context)

    # Test operation
    result = facade.operation()

    # Verify
    assert result == {"status": "completed", "ok": True}
    mock_file_extract.return_value.request.assert_called_once()
    mock_find_document.return_value.request.assert_called_once()
    mock_external_api.return_value.request.assert_not_called()
    mock_update_document.return_value.request.assert_not_called()

def test_integration_facade_update_failure(
    mock_context,
    mock_file_extract,
    mock_find_document,
    mock_external_api,
    mock_update_document
):
    # Setup mocks
    mock_find_document.return_value.request.return_value = None  # Document not found
    mock_external_api.return_value.request.side_effect = [
        {  # First call - item details
            "id": "MLA123",
            "title": "Test Item",
            "price": 100.0,
            "currency_id": "ARS"
        },
        {  # Second call - currency details
            "id": "ARS",
            "symbol": "$",
            "description": "Peso argentino"
        }
    ]
    mock_update_document.return_value.request.return_value = False  # Update failed

    # Create facade with required parameter
    parameter = {
        "name_file": "test_file",
        "format": "jsonl",
        "encoding": "utf-8",
        "separator": ","
    }
    facade = IntegrationApiFacade(parameter)
    facade.set_context(mock_context)

    # Test operation
    result = facade.operation()

    # Verify
    assert result == {"status": "completed", "ok": True}  # Still returns success as per requirements
    mock_file_extract.return_value.request.assert_called_once()
    mock_find_document.return_value.request.assert_called_once()
    assert mock_external_api.return_value.request.call_count == 2
    mock_update_document.return_value.request.assert_called_once() 