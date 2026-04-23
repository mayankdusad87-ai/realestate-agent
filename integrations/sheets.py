"""
Read data from Excel files and Google Sheets.

Provides a unified interface for agents to consume MIS data regardless
of whether the source is a local .xlsx file or a Google Sheet.
Both functions return a list of dicts (one per data row).
"""
import logging
from pathlib import Path

import openpyxl

logger = logging.getLogger(__name__)

_SUPPORTED_EXTENSIONS = {".xlsx", ".xlsm"}


def read_excel(
    file_path: str | Path,
    *,
    sheet_name: str | None = None,
    header_row: int = 1,
) -> list[dict[str, str]]:
    """Read an Excel workbook and return rows as a list of dicts.

    Args:
        file_path: Path to a .xlsx or .xlsm file.
        sheet_name: Worksheet name. Defaults to the active sheet.
        header_row: 1-indexed row number containing column headers.

    Returns:
        List of dicts keyed by header values. Empty cells become "".
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")
    if path.suffix not in _SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Use .xlsx or .xlsm."
        )

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        ws = wb[sheet_name] if sheet_name else wb.active
        rows = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()

    if len(rows) < header_row:
        return []

    headers = [
        str(h or f"col_{i}") for i, h in enumerate(rows[header_row - 1])
    ]
    return [
        dict(zip(headers, (str(v) if v is not None else "" for v in row)))
        for row in rows[header_row:]
        if any(v is not None for v in row)
    ]


def read_google_sheet(
    spreadsheet_id: str,
    *,
    worksheet_name: str | None = None,
    credentials_path: str | None = None,
) -> list[dict[str, str]]:
    """Read a Google Sheet and return rows as a list of dicts.

    Requires the optional ``gspread`` and ``google-auth`` packages.

    Args:
        spreadsheet_id: Google Sheets document ID.
        worksheet_name: Worksheet name. Defaults to the first sheet.
        credentials_path: Path to a Google service-account JSON file.
            Falls back to ``config.GOOGLE_CREDENTIALS_PATH`` if not provided.

    Returns:
        List of dicts keyed by the first row (header).
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as exc:
        raise ImportError(
            "Google Sheets support requires 'gspread' and 'google-auth'. "
            "Install with: pip install gspread google-auth"
        ) from exc

    if not credentials_path:
        from config import GOOGLE_CREDENTIALS_PATH

        credentials_path = GOOGLE_CREDENTIALS_PATH

    if not credentials_path:
        raise ValueError(
            "No credentials path provided. Set GOOGLE_CREDENTIALS_PATH in "
            "config.py or pass credentials_path directly."
        )

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    gc = gspread.authorize(creds)

    spreadsheet = gc.open_by_key(spreadsheet_id)
    ws = (
        spreadsheet.worksheet(worksheet_name)
        if worksheet_name
        else spreadsheet.sheet1
    )
    return ws.get_all_records()
