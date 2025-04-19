import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def connect_to_gsheet(sheet_name: str):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scope
    )
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name)
    return sheet

def read_receivers():
    sheet = connect_to_gsheet("job-alert-settings")
    worksheet = sheet.worksheet("emails")
    data = worksheet.get_all_records()
    return data

def write_receivers(data):
    sheet = connect_to_gsheet("job-alert-settings")
    worksheet = sheet.worksheet("emails")
    worksheet.clear()
    worksheet.append_row(["이메일 주소", "활성화"])  # 헤더
    for row in data:
        worksheet.append_row([row["이메일 주소"], row["활성화"]])
