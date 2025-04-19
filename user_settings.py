import streamlit as st
from datetime import datetime
from google_sheets_helper import (
    read_receivers, write_receivers,
    read_keywords, write_keywords,
    read_notification_settings, write_notification_settings
)

class UserSettings:
    def __init__(self):
        # 이메일 로그인 정보 (secrets에서만 유지)
        if 'email_settings' not in st.session_state:
            try:
                st.session_state.email_settings = {
                    'sender_email': st.secrets["SENDER_EMAIL"],
                    'sender_password': st.secrets["SENDER_PASSWORD"],
                }
            except Exception as e:
                st.warning("이메일 설정이 필요합니다. Streamlit Secrets에 SENDER_EMAIL, SENDER_PASSWORD를 설정해주세요.")
                st.session_state.email_settings = {
                    'sender_email': "",
                    'sender_password': "",
                }

        # 수신자 초기화
        if 'receivers' not in st.session_state:
            st.session_state.receivers = read_receivers()

        # 키워드 초기화
        if 'keywords' not in st.session_state:
            st.session_state.keywords = read_keywords()

        # 알림 설정 초기화
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = read_notification_settings()

        # 수동 채용공고는 로컬 상태에만 저장
        if 'manual_jobs' not in st.session_state:
            st.session_state.manual_jobs = []

    def get_email_settings(self):
        return st.session_state.email_settings

    def get_notification_settings(self):
        return st.session_state.notification_settings

    def get_keywords(self):
        return st.session_state.keywords

    def get_receivers(self):
        return st.session_state.receivers

    def get_manual_jobs(self):
        return st.session_state.manual_jobs

    def add_manual_job(self, url):
        st.session_state.manual_jobs.append({
            'company': "수동 추가",
            'company_logo': "https://via.placeholder.com/50",
            'title': "수동 추가된 채용공고",
            'description': url,
            'link': url,
            'career': "경력무관",
            'deadline': "상시채용",
            'added_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def update_notification_settings(self, times, frequency):
        converted_times = [self._convert_to_24h_format(t) for t in times]
        updated = {
            'times': converted_times,
            'frequency': frequency
        }
        st.session_state.notification_settings = updated
        write_notification_settings(updated)

    def update_keywords(self, keywords):
        cleaned = [k.strip() for k in keywords if k.strip()]
        st.session_state.keywords = cleaned
        write_keywords(cleaned)

    def update_receivers(self, receivers):
        st.session_state.receivers = receivers
        write_receivers(receivers)

    def _convert_to_24h_format(self, time_str):
        """시간을 24시간 형식으로 변환"""
        if "오전" in time_str:
            time = time_str.replace("오전 ", "")
            hour, minute = map(int, time.split(":"))
            if hour == 12:
                hour = 0
        else:  # 오후
            time = time_str.replace("오후 ", "")
            hour, minute = map(int, time.split(":"))
            if hour != 12:
                hour += 12
        return f"{hour:02d}:{minute:02d}"
