import streamlit as st
from datetime import datetime
from google_sheets_helper import (
    load_user_settings,
    save_user_settings,
    read_admin_keywords
)

class UserSettings:
    def __init__(self):
        self.email = None
        self.settings = None
        self.keywords = read_admin_keywords()

    def set_email(self, email):
        self.email = email
        self.settings = load_user_settings(email)

    def is_active(self):
        if self.settings:
            return self.settings.get("active", False)
        return False

    def get_keywords(self):
        return self.keywords

    def get_notification_settings(self):
        if not self.settings:
            return {
                "times": ["09:00"],
                "frequency": "하루 1회",
                "career": "경력"
            }
        return {
            "times": self.settings.get("times", ["09:00"]),
            "frequency": self.settings.get("frequency", "하루 1회"),
            "career": self.settings.get("career", "경력")
        }

    def update_notification_settings(self, times, frequency, career):
        if self.email:
            active = self.settings.get("active", True) if self.settings else True
            save_user_settings(self.email, active, times, frequency, career)
            self.settings = load_user_settings(self.email)

    def set_active(self, active):
        if self.email:
            current = self.get_notification_settings()
            save_user_settings(
                self.email, active,
                current["times"],
                current["frequency"],
                current["career"]
            )
            self.settings = load_user_settings(self.email)

    def get_email(self):
        return self.email

    def get_manual_jobs(self):
        if 'manual_jobs' not in st.session_state:
            st.session_state.manual_jobs = []
        return st.session_state.manual_jobs
    def get_receivers(self):
        return st.session_state.receivers
    
    def update_receivers(self, receivers):
        st.session_state.receivers = receivers
        write_receivers(receivers)
    
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

