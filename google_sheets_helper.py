import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# --- 인증 및 시트 연결 ---
@st.cache_data(ttl=60) # 1분 동안 캐싱
def connect_to_sheet(sheet_name, tab_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    return client.open(sheet_name).worksheet(tab_name)

# --- 사용자 설정 불러오기 ---
def load_user_settings(email):
    sheet = connect_to_sheet("job-alert-settings", "userinfos")
    data = sheet.get_all_records()
    for row in data:
        if row["이메일 주소"] == email:
            return {
                "email": row["이메일 주소"],
                "active": str(row.get("활성화", "")).upper() == "TRUE",
                "times": row.get("알림 시간", "").split(","),
                "frequency": row.get("알림 빈도", "하루 1회"),
                "career": row.get("경력 구분", "경력")
            }
    return None

# --- 사용자 설정 저장 (신규/업데이트) ---
def save_user_settings(email, active, times, frequency, career):
    sheet = connect_to_sheet("job-alert-settings", "userinfos")
    data = sheet.get_all_records()
    times_str = ",".join(times)

    for idx, row in enumerate(data):
        if row["이메일 주소"] == email:
            sheet.update(f"B{idx+2}", [[str(active).upper()]])
            sheet.update(f"C{idx+2}", [[times_str]])
            sheet.update(f"D{idx+2}", [[frequency]])
            sheet.update(f"E{idx+2}", [[career]])
            return

    # 신규 추가
    sheet.append_row([email, str(active).upper(), times_str, frequency, career])

# --- 크롤링 필터용 키워드 목록 불러오기 ---
def read_admin_keywords():
    sheet = connect_to_sheet("job-alert-settings", "keywords")
    return [row[0] for row in sheet.get_all_values()[1:] if row and row[0].strip()]

@st.cache_data(ttl=60)  # ✅ 60초 동안 캐싱
def get_keywords():
    return read_admin_keywords()
    
# --- 크롤링 대상 기업 정보 불러오기 ---
def read_company_settings():
    sheet = connect_to_sheet("job-alert-settings", "settings")
    return sheet.get_all_records()
    
@st.cache_data(ttl=60)  # ✅ 60초 동안 캐싱
def get_company_settings():
    return read_company_settings()
