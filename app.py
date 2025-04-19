import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from job_fetcher import JobFetcher
from email_sender import EmailSender
from scheduler import JobScheduler
from user_settings import UserSettings


# 페이지 설정
st.set_page_config(
    page_title="기획자 채용 알리미",
    page_icon="💼",
    layout="wide"
)


# 간단한 디버그 (secrets 확인)
if st.secrets:
    st.sidebar.success("Secrets 설정이 완료되었습니다!")
    
# CSS 스타일
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
    # 초기화
    user_settings = UserSettings()
    job_fetcher = JobFetcher()
    email_sender = EmailSender()
    scheduler = JobScheduler(job_fetcher, email_sender, user_settings)
    
    # 헤더
    st.title("🎯 기획자 채용 알리미")
    
    # 탭 생성
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
        
        # 필터 섹션
        st.sidebar.title("필터 설정")
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
        
        # 채용 공고 표시
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
        
        # 수신자 관리
        st.write("#### 📧 이메일 등록 및 수신 거부")
        
        new_email = st.text_input("이메일 주소 입력", placeholder="example@domain.com")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📩 이메일 추가", use_container_width=True):
                receivers = user_settings.get_receivers()
                email_list = [r["이메일 주소"] for r in receivers]

                if not new_email:
                    st.warning("이메일을 입력해주세요.")
                elif not notification_times:
                    st.warning("알림 받을 시간을 먼저 선택해주세요.")
                elif new_email in email_list:
                    st.warning("이미 등록된 이메일입니다.")
                elif "@" not in new_email or "." not in new_email:
                    st.error("올바른 이메일 형식이 아닙니다.")
                else:
                    receivers.append({"이메일 주소": new_email, "활성화": True})
                    user_settings.update_receivers(receivers)
                    st.success("이메일이 추가되었습니다.")
        
        with col2:
            if st.button("🛑 수신 거부", use_container_width=True):
                receivers = user_settings.get_receivers()
                updated = False
        
                for r in receivers:
                    if r["이메일 주소"] == new_email:
                        if not r["활성화"]:
                            st.info("이미 수신 거부된 이메일입니다.")
                        else:
                            r["활성화"] = False
                            updated = True
                            st.success("수신 거부 처리되었습니다.")
                        break
                else:
                    st.warning("등록되지 않은 이메일입니다.")
        
                if updated:
                    user_settings.update_receivers(receivers)
    # 알림 시간 설정
    st.write("#### 📅 알림 시간 설정")
    col1, col2 = st.columns(2)
    with col1:
        notification_times = st.multiselect(
            "알림 받을 시간 선택 (최대 2회)",
            [
                "오전 8:30", "오전 9:00", "오전 10:00",
                "오후 2:00", "오후 6:00", "오후 9:00"
            ],
            default=["오전 9:00"],
            max_selections=2
        )
        with col2:
            notification_frequency = st.radio(
                "알림 빈도",
                ["하루 1회", "하루 2회"],
                index=0
            )
        
        # 키워드 설정
        st.write("#### 🔎 키워드 설정")
        keywords = st.text_area(
            "검색 키워드 (줄바꿈으로 구분)",
            "\n".join(user_settings.get_keywords())
        ).split("\n")
        
        # 수동 URL 추가
        st.write("#### 🔗 채용공고 수동 추가")
        col3, col4 = st.columns([3, 1])
        with col3:
            manual_url = st.text_input("채용공고 URL")
        with col4:
            if st.button("추가", use_container_width=True):
                if manual_url:
                    if not manual_url.startswith(('http://', 'https://')):
                        st.error("유효한 URL을 입력해주세요.")
                    else:
                        user_settings.add_manual_job(manual_url)
                        st.success("채용공고가 추가되었습니다!")
  
        if st.button("💾 설정 저장", type="primary"):
            user_settings.update_notification_settings(
                times=notification_times,
                frequency=notification_frequency
            )
            user_settings.update_keywords([k.strip() for k in keywords if k.strip()])
            st.success("설정이 저장되었습니다!")
            scheduler.restart()
            
if __name__ == "__main__":
    main()
