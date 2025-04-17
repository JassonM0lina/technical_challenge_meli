import pytest
from unittest.mock import patch, mock_open
from modules.fetch_integrate.infraestructure.integration_connection import FileExtract

@pytest.mark.parametrize("file_content,parameters,expected", [
    # JSONL format
    (
        '{"site": "MLA", "id": "MLA123"}\n{"site": "MLA", "id": "MLA456"}',
        {
            "file_location": "test_file",
            "format": "jsonl",
            "encoding": "utf-8",
            "separator": ";"
        },
        [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
    ),
    # CSV format with comma separator
    (
        "site,id\nMLA,MLA123\nMLA,MLA456",
        {
            "file_location": "test_file",
            "format": "csv",
            "encoding": "utf-8",
            "separator": ","
        },
        [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
    ),
    # CSV format with semicolon separator
    (
        "site;id\nMLA;MLA123\nMLA;MLA456",
        {
            "file_location": "test_file",
            "format": "csv",
            "encoding": "utf-8",
            "separator": ";"
        },
        [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
    ),
    # TXT format with comma separator
    (
        "site,id\nMLA,MLA123\nMLA,MLA456",
        {
            "file_location": "test_file",
            "format": "txt",
            "encoding": "utf-8",
            "separator": ","
        },
        [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
    ),
    # TXT format with semicolon separator
    (
        "site;id\nMLA;MLA123\nMLA;MLA456",
        {
            "file_location": "test_file",
            "format": "txt",
            "encoding": "utf-8",
            "separator": ";"
        },
        [
            {"site": "MLA", "id": "MLA123"},
            {"site": "MLA", "id": "MLA456"}
        ]
    )
])
def test_file_extract_with_different_formats(file_content, parameters, expected):
    with patch("builtins.open", mock_open(read_data=file_content)):
        file_extract = FileExtract(parameters)
        result = list(file_extract.request())  # Convert generator to list
        
        assert result == expected
        assert all(isinstance(item, dict) for item in result)
        assert all("site" in item and "id" in item for item in result)

def test_file_extract_with_invalid_format():
    with patch("builtins.open", mock_open(read_data="some content")):
        parameters = {
            "file_location": "test_file",
            "format": "invalid",
            "encoding": "utf-8",
            "separator": ","
        }
        file_extract = FileExtract(parameters)
        with pytest.raises(ValueError, match="Unsupported format: invalid"):
            list(file_extract.request())  # Convert generator to list

def test_file_extract_with_empty_file():
    with patch("builtins.open", mock_open(read_data="")):
        parameters = {
            "file_location": "test_file",
            "format": "jsonl",
            "encoding": "utf-8",
            "separator": ","
        }
        file_extract = FileExtract(parameters)
        result = list(file_extract.request())  # Convert generator to list
        assert result == [] 