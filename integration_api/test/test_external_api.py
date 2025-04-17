import pytest
from unittest.mock import patch, MagicMock
from modules.fetch_integrate.infraestructure.integration_connection import RequestExternalResource
import os

@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get:
        yield mock_get

@pytest.fixture
def external_api():
    return RequestExternalResource()

@pytest.fixture
def mock_environment(monkeypatch):
    # Mock environment variables for testing
    monkeypatch.setenv('MELI_API_HOST', 'http://meli-api:5000')

@pytest.mark.parametrize("url,params,expected_response", [
    (
        "http://meli-api:5000/items/items",
        {
            "ids": "MLA750925229,MLA845041373",
            "attributes": "name,stock,price,category_id,currency_id"
        },
        [
            {
                "name": "MLA750925229",
                "stock": 23,
                "price": 52.48,
                "category_id": "CAT189",
                "currency_id": "CUR998"
            },
            {
                "name": "MLA845041373",
                "stock": 15,
                "price": 75.99,
                "category_id": "CAT189",
                "currency_id": "CUR998"
            }
        ]
    ),
    (
        "http://meli-api:5000/categories",
        {"ids": "CAT189"},
        [
            {
                "id": "CAT189",
                "name": "Test Category",
                "path_from_root": [
                    {"id": "CAT1", "name": "Root Category"},
                    {"id": "CAT189", "name": "Test Category"}
                ]
            }
        ]
    ),
    (
        "http://meli-api:5000/currencies",
        {"ids": "CUR998"},
        [
            {
                "id": "CUR998",
                "symbol": "$",
                "description": "Peso argentino",
                "decimal_places": 2
            }
        ]
    )
])
def test_external_api_success(mock_requests, external_api, url, params, expected_response):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = expected_response
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Make request
    response = external_api.request(url, params)

    # Verify
    mock_requests.assert_called_once_with(url, params=params)
    assert response == expected_response

def test_external_api_connection_error(mock_requests, external_api):
    # Setup mock to raise connection error
    mock_requests.side_effect = ConnectionError("Connection failed")

    # Make request and verify error
    with pytest.raises(Exception, match="Error occurred: Connection failed"):
        external_api.request(
            "http://meli-api:5000/items/items",
            {"ids": "MLA750925229", "attributes": "name,price,category_id"}
        )

def test_external_api_invalid_response(mock_requests, external_api):
    # Setup mock with invalid response
    mock_response = MagicMock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Make request and verify error
    with pytest.raises(Exception, match="Error occurred: Invalid JSON"):
        external_api.request(
            "http://meli-api:5000/items/items",
            {"ids": "MLA750925229", "attributes": "name,price,category_id"}
        )

def test_external_api_http_error(mock_requests, external_api):
    # Setup mock with HTTP error
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests.return_value = mock_response

    # Make request and verify error
    with pytest.raises(Exception, match="Error occurred: HTTP error occurred: 404"):
        external_api.request(
            "http://meli-api:5000/items/items",
            {"ids": "MLA750925229", "attributes": "name,price,category_id"}
        )

def test_external_api_with_attributes_filter(mock_requests, external_api):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
                "name": "Peso argentino",
                "description": "Moneda oficial de Argentina",
                "symbol": "$",
                "code": "ARS"
            }
    
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Make request with attribute filter
    response = external_api.request(
        "http://meli-api:5000/currencies",
        {"ids": "ARS,USD", "attributes": "name,description,symbol,code"},
        ["description"] 
    )

    # Verify
    assert response == {"description": "Moneda oficial de Argentina"}
            
    

def test_external_api_environment_variable(mock_requests, external_api, mock_environment):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "name": "MLA750925229",
            "stock": 23,
            "price": 52.48,
            "category_id": "CAT189",
            "currency_id": "CUR998"
        }
    ]
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Make request using environment variable
    base_url = os.getenv('MELI_API_HOST', 'http://meli-api:5000')
    url = f"{base_url}/items/items"
    
    response = external_api.request(
        url,
        {"ids": "MLA750925229", "attributes": "name,stock,price,category_id,currency_id"}
    )

    # Verify
    mock_requests.assert_called_once_with(url, params={"ids": "MLA750925229", "attributes": "name,stock,price,category_id,currency_id"})
    assert response == [
        {
            "name": "MLA750925229",
            "stock": 23,
            "price": 52.48,
            "category_id": "CAT189",
            "currency_id": "CUR998"
        }
    ] 