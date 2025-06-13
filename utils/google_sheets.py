# utils/google_sheets.py
import os
import base64
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_sheets_service():
    b64_creds = os.environ.get("GOOGLE_SHEETS_CREDS_B64")
    if not b64_creds:
        raise Exception("Missing GOOGLE_SHEETS_CREDS_B64 environment variable")

    json_creds = base64.b64decode(b64_creds).decode('utf-8')
    creds_dict = json.loads(json_creds)

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    service = build("sheets", "v4", credentials=credentials)
    return service.spreadsheets()
