import streamlit as st
from datetime import datetime

class UserSettings:
    def __init__(self):
        # 이메일 설정 초기화
        if 'email_settings' not in st.session_state:
            try:
                st.session_state.email_settings = {
                    'sender_email': st.secrets["SENDER_EMAIL"],
                    'sender_password': st.secrets["SENDER_PASSWORD"],
                }
            except Exception as e:
                st.warning("이메일 설정이 필요합니다. Settings에서 Secrets를 설정해주세요.")
                st.session_state.email_settings = {
                    'sender_email': "",
                    'sender_password': "",
                }
        
        # 알림 설정 초기화 (24시간 형식으로 변경)
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = {
                'times': ["09:00"],  # 24시간 형식으로 변경
                'frequency': "하루 1회"
            }
        
        # 키워드 초기화
        if 'keywords' not in st.session_state:
            st.session_state.keywords = [
                "기획", "PM", "프로덕트 매니저",
                "서비스기획", "비즈니스기획", "플랫폼기획"
            ]
        
        # 수신자 목록 초기화
        if 'receivers' not in st.session_state:
            st.session_state.receivers = [
                {"이메일 주소": st.secrets.get("RECEIVER_EMAIL", ""), "활성화": True}
            ]
        
        # 수동 추가된 채용공고 초기화
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
        st.session_state.notification_settings = {
            'times': times,
            'frequency': frequency
        }
    
    def update_keywords(self, keywords):
        st.session_state.keywords = keywords
    
    def update_receivers(self, receivers):
        st.session_state.receivers = receivers

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

    def update_notification_settings(self, times, frequency):
        # 시간을 24시간 형식으로 변환
        converted_times = [self._convert_to_24h_format(time) for time in times]
        st.session_state.notification_settings = {
            'times': converted_times,
            'frequency': frequency
        }
