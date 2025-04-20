import streamlit as st
import pandas as pd
from datetime import datetime
from job_fetcher import JobFetcher
from email_sender import EmailSender
from scheduler import JobScheduler
from user_settings import UserSettings



st.set_page_config(
    page_title="기획자 채용 알리미",
    page_icon="💼",
    layout="wide"
)

# ✅ 그다음에 디버깅 코드나 gspread 등 넣기
import gspread
from google.oauth2.service_account import Credentials

try:
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("job-alert-settings")
    tabs = [ws.title for ws in sheet.worksheets()]
    st.sidebar.success(f"접속 성공 ✅ 시트 탭 목록: {tabs}")
except Exception as e:
    st.sidebar.error(f"접속 실패 ❌: {e}")

if st.secrets:
    st.sidebar.success("Secrets 설정이 완료되었습니다!")

st.markdown("""
<style>
.job-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #eee;
    margin: 10px 0;
    display: flex;
    align-items: start;
}
.company-logo {
    width: 50px;
    height: 50px;
    margin-right: 15px;
    object-fit: contain;
}
.job-content {
    flex-grow: 1;
}
.company-tag {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: white;
    margin-right: 8px;
}
.deadline-tag {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    background-color: #f0f0f0;
    color: #666;
}
.company-naver { background-color: #03C75A; }
.company-naverfinancial { background-color: #1EC800; }
.company-samsung { background-color: #1428A0; }
.company-google { background-color: #4285F4; }
.company-skt { background-color: #EA002C; }
</style>
""", unsafe_allow_html=True)

def main():
      # ✅ 1. 필터 변수 먼저 선언 (탭 바깥)
    companies = st.sidebar.multiselect(
        "회사 선택",
        ["네이버", "네이버파이낸셜", "삼성전자", "구글코리아", "SKT"],
        default=["네이버", "네이버파이낸셜"]
    )
    career_filter = st.sidebar.multiselect(
        "경력 선택",
        ["경력", "신입/경력", "경력무관"],
        default=["경력", "신입/경력"]
    )   
            # ✅ 2. 기존 main 코드 진행
    user_settings = UserSettings()
    job_fetcher = JobFetcher()
    email_sender = EmailSender()
    scheduler = JobScheduler(job_fetcher, email_sender, user_settings)

    st.title("🎯 기획자 채용 알리미")
    tab1, tab2 = st.tabs(["📋 채용 공고", "⚙️ 설정"])

    with tab1:
        col1, col2 = st.columns([3,1])
        with col1:
            st.write("### 실시간 채용 공고")
        with col2:
            if st.button("🔄 지금 검색하기", use_container_width=True):
                with st.spinner("채용 정보를 검색중입니다..."):
                    jobs = job_fetcher.fetch_all_jobs(user_settings.get_keywords())
                    if jobs:
                        st.session_state.last_check = datetime.now()
                        st.session_state.last_jobs = jobs

        st.sidebar.title("필터 설정")
        career_filter = st.sidebar.multiselect(
            "경력 선택",
            ["경력", "신입/경력", "경력무관"],
            default=["경력", "신입/경력"]
        )

        if 'last_jobs' in st.session_state:
            all_jobs = st.session_state.last_jobs + user_settings.get_manual_jobs()
            filtered_jobs = [
                job for job in all_jobs
                if job['company'] in companies and
                job.get('career', '경력무관') in career_filter
            ]

            for job in filtered_jobs:
                company_class = job['company'].lower().replace(" ", "")
                st.markdown(f"""
                <div class="job-card">
                    <img src="{job['company_logo']}" class="company-logo" onerror="this.src='https://via.placeholder.com/50'">
                    <div class="job-content">
                        <span class="company-tag company-{company_class}">{job['company']}</span>
                        <span class="deadline-tag">마감일: {job.get('deadline', '상시채용')}</span>
                        <h3>{job['title']}</h3>
                        <p>{job['description'][:200]}...</p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #666;">{job.get('career', '경력무관')}</span>
                            <a href="{job['link']}" target="_blank">자세히 보기 →</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.write("### ⚙️ 알림 설정")

        email = st.text_input("이메일 주소 입력", placeholder="example@domain.com")
        if email:
            user_settings.set_email(email)
            current = user_settings.get_notification_settings()

            times = st.multiselect(
                "알림 받을 시간 (최대 2개)",
                ["오전 8:30", "오전 9:00", "오전 10:00", "오후 2:00", "오후 6:00", "오후 9:00"],
                default=current["times"],
                max_selections=2
            )
            frequency = st.radio("알림 빈도", ["하루 1회", "하루 2회"], index=0 if current["frequency"] == "하루 1회" else 1)
            career = st.selectbox("경력 구분", ["경력", "신입/경력", "경력무관"], index=["경력", "신입/경력", "경력무관"].index(current["career"]))

            if st.button("💾 설정 저장", type="primary"):
                user_settings.update_notification_settings(times, frequency, career)
                st.success("설정이 저장되었습니다!")
                scheduler.restart()

if __name__ == "__main__":
    main()
