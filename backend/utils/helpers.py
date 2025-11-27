import os
import json
import gspread
from google.oauth2.service_account import Credentials
from backend.models.schemas import Contact

def save_contact_to_sheet(contact: Contact):
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1
    sheet.append_row([contact.name, contact.email, contact.message])
