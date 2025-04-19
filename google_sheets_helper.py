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

def read_keywords():
    sheet = connect_to_gsheet("job-alert-settings")
    ws = sheet.worksheet("keywords")
    return [row[0] for row in ws.get_all_values()[1:]]

def write_keywords(keywords):
    sheet = connect_to_gsheet("job-alert-settings")
    ws = sheet.worksheet("keywords")
    ws.clear()
    ws.append_row(["키워드"])
    for k in keywords:
        ws.append_row([k])

def read_notification_settings():
    sheet = connect_to_gsheet("job-alert-settings")
    ws = sheet.worksheet("notification")
    values = ws.get_all_values()[1:]
    times = [v[0] for v in values]
    frequency = values[0][1] if values else "하루 1회"
    return {"times": times, "frequency": frequency}

def write_notification_settings(data):
    sheet = connect_to_gsheet("job-alert-settings")
    ws = sheet.worksheet("notification")
    ws.clear()
    ws.append_row(["시간", "빈도"])
    for time in data["times"]:
        ws.append_row([time, data["frequency"]])

def read_notification_settings():
    sheet = connect_to_gsheet("job-alert-settings")
    ws = sheet.worksheet("notification")
    values = ws.get_all_values()[1:]  # 첫 행은 헤더니까 제외

    times = []
    frequency = "하루 1회"

    for row in values:
        if len(row) >= 1:
            normalized_time = normalize_time_format(row[0])
            times.append(normalized_time)
        if len(row) >= 2:
            frequency = row[1]

    return {
        "times": times,
        "frequency": frequency
    }
