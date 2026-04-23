"""
Tests for integrations.sheets — Excel reading.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from integrations.sheets import read_excel


def test_read_excel_file_not_found():
    with pytest.raises(FileNotFoundError, match="not found"):
        read_excel("/nonexistent/path.xlsx")


def test_read_excel_unsupported_format(tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError, match="Unsupported file format"):
        read_excel(csv_file)


@patch("integrations.sheets.openpyxl")
def test_read_excel_returns_list_of_dicts(mock_openpyxl, tmp_path):
    # Create a real .xlsx file path (content mocked)
    xlsx = tmp_path / "test.xlsx"
    xlsx.touch()

    mock_ws = MagicMock()
    mock_ws.iter_rows.return_value = [
        ("Name", "City", "Price"),
        ("Project A", "Mumbai", "15000"),
        ("Project B", "Pune", "12000"),
        (None, None, None),  # empty row — should be skipped
    ]

    mock_wb = MagicMock()
    mock_wb.active = mock_ws
    mock_wb.__getitem__ = MagicMock(return_value=mock_ws)
    mock_openpyxl.load_workbook.return_value = mock_wb

    rows = read_excel(xlsx)

    assert len(rows) == 2
    assert rows[0] == {"Name": "Project A", "City": "Mumbai", "Price": "15000"}
    assert rows[1] == {"Name": "Project B", "City": "Pune", "Price": "12000"}


@patch("integrations.sheets.openpyxl")
def test_read_excel_with_named_sheet(mock_openpyxl, tmp_path):
    xlsx = tmp_path / "test.xlsx"
    xlsx.touch()

    mock_ws = MagicMock()
    mock_ws.iter_rows.return_value = [
        ("Col1", "Col2"),
        ("val1", "val2"),
    ]

    mock_wb = MagicMock()
    mock_wb.__getitem__ = MagicMock(return_value=mock_ws)
    mock_openpyxl.load_workbook.return_value = mock_wb

    rows = read_excel(xlsx, sheet_name="Sheet2")

    mock_wb.__getitem__.assert_called_with("Sheet2")
    assert len(rows) == 1


@patch("integrations.sheets.openpyxl")
def test_read_excel_empty_file(mock_openpyxl, tmp_path):
    xlsx = tmp_path / "empty.xlsx"
    xlsx.touch()

    mock_ws = MagicMock()
    mock_ws.iter_rows.return_value = []

    mock_wb = MagicMock()
    mock_wb.active = mock_ws
    mock_openpyxl.load_workbook.return_value = mock_wb

    assert read_excel(xlsx) == []


@patch("integrations.sheets.openpyxl")
def test_read_excel_none_headers_get_default_names(mock_openpyxl, tmp_path):
    xlsx = tmp_path / "test.xlsx"
    xlsx.touch()

    mock_ws = MagicMock()
    mock_ws.iter_rows.return_value = [
        ("Name", None, "Price"),
        ("A", "B", "C"),
    ]

    mock_wb = MagicMock()
    mock_wb.active = mock_ws
    mock_openpyxl.load_workbook.return_value = mock_wb

    rows = read_excel(xlsx)
    assert "col_1" in rows[0]
    assert rows[0]["col_1"] == "B"
