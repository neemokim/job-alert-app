# ✅ 1단계: 사용자 설정 UI 분리 (Streamlit)
# 파일: app.py 또는 user_ui.py 내 탭 또는 섹션으로 추가할 수 있음

import streamlit as st
from user_settings import UserSettings
from job_fetcher import JobFetcher
from email_sender import EmailSender

user_settings = UserSettings()
job_fetcher = JobFetcher()
email_sender = EmailSender()

st.header("⚙️ 알림 설정")

# --- 이메일 입력 ---
new_email = st.text_input("이메일 주소 입력", placeholder="example@domain.com")

# --- 알림 시간 설정 ---
notification_times = st.multiselect(
    "알림 받을 시간 선택 (최대 2회)",
    ["오전 8:30", "오전 9:00", "오전 10:00", "오후 2:00", "오후 6:00", "오후 9:00"],
    max_selections=2,
    key="ntimes"
)

notification_frequency = st.radio(
    "알림 빈도",
    ["하루 1회", "하루 2회"],
    index=0,
    key="freq"
)

career_option = st.selectbox("신입/경력 여부 선택", ["경력", "신입/경력", "경력무관"], key="career")

# --- 신청 버튼 ---
if st.button("📩 알림 신청하기"):
    if not new_email or "@" not in new_email:
        st.warning("유효한 이메일 주소를 입력하세요.")
    elif not notification_times:
        st.warning("알림 시간을 1개 이상 선택하세요.")
    else:
        try:
            receivers = user_settings.get_receivers()
        except Exception as e:
            st.error(f"알림 신청 정보를 불러올 수 없습니다: {e}")
            receivers = []

        exists = any(r.get("이메일 주소") == new_email for r in receivers)
        if exists:
            st.warning("이미 등록된 이메일입니다.")
        else:
            receivers.append({
                "이메일 주소": new_email,
                "알림 시간": ",".join(notification_times),
                "빈도": notification_frequency,
                "신입/경력": career_option,
                "활성화": True
            })
            user_settings.update_receivers(receivers)
            st.success("알림 신청이 완료되었습니다.")

# --- 수신 거부 ---
st.divider()
st.subheader("🛑 수신 거부")
unsub_email = st.text_input("수신 거부할 이메일 입력", key="unsubscribe")
if st.button("❌ 수신 거부"):
    try:
        receivers = user_settings.get_receivers()
    except Exception as e:
        st.error(f"수신 거부 정보를 불러올 수 없습니다: {e}")
        receivers = []

    found = False
    for r in receivers:
        if r.get("이메일 주소") == unsub_email:
            r["활성화"] = False
            found = True
    if found:
        user_settings.update_receivers(receivers)
        st.success("수신 거부 처리되었습니다.")
    else:
        st.warning("등록되지 않은 이메일입니다.")

# --- 수동 발송 ---
st.divider()
if st.button("🔄 지금 채용 공고 발송"):
    with st.spinner("채용 공고 수집 및 발송중..."):
        keywords = user_settings.get_keywords()
        jobs = job_fetcher.fetch_all_jobs(keywords)
        try:
            receivers = user_settings.get_receivers()
        except Exception as e:
            st.error(f"수신자 목록을 불러올 수 없습니다: {e}")
            receivers = []

        active_receivers = [r for r in receivers if r.get("활성화")]
        if jobs and active_receivers:
            for r in active_receivers:
                email_sender.send_email(r["이메일 주소"], jobs)
            st.success("모든 사용자에게 이메일이 발송되었습니다!")
        else:
            st.info("보낼 공고나 대상자가 없습니다.")
