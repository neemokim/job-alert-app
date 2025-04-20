import schedule
import time
from datetime import datetime
from google_sheets_helper import load_user_settings

class JobScheduler:
    def __init__(self, job_fetcher, email_sender, user_settings):
        self.job_fetcher = job_fetcher
        self.email_sender = email_sender
        self.user_settings = user_settings
        self.jobs = []
        self.restart()

    def _run_job(self, email):
        user_setting = load_user_settings(email)
        if not user_setting or not user_setting.get("active", False):
            return

        keywords = self.user_settings.get_keywords()
        jobs = self.job_fetcher.fetch_all_jobs(keywords)
        filtered_jobs = [
            job for job in jobs
            if job.get("career", "경력") == user_setting.get("career", "경력")
        ]
        self.email_sender.send_email(email, filtered_jobs)

    def restart(self):
        schedule.clear()
        self.jobs = []

        sheet = self._get_all_users()
        for user in sheet:
            if not user.get("활성화") or not user.get("알림 시간"):
                continue
            times = user["알림 시간"].split(",")
            for t in times:
                schedule.every().day.at(self._normalize_time(t)).do(self._run_job, email=user["이메일 주소"])

    def _normalize_time(self, time_str):
        """'오전 9:00' 또는 '오후 1:30' 같은 시간 문자열을 'HH:MM' 포맷으로 바꿔줌"""
        if "오전" in time_str:
            time = time_str.replace("오전 ", "")
            hour, minute = map(int, time.split(":"))
            if hour == 12:
                hour = 0
        elif "오후" in time_str:
            time = time_str.replace("오후 ", "")
            hour, minute = map(int, time.split(":"))
            if hour != 12:
                hour += 12
        else:
            hour, minute = map(int, time_str.strip().split(":"))  # 24시간 포맷
        return f"{hour:02d}:{minute:02d}"


    def _get_all_users(self):
        from google_sheets_helper import connect_to_sheet
        sheet = connect_to_sheet("job-alert-settings", "userinfos")
        return sheet.get_all_records()

    def run_pending(self):
        while True:
            schedule.run_pending()
            time.sleep(30)
