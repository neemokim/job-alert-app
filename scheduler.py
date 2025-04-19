import schedule
import time
import threading
import logging
from datetime import datetime

class JobScheduler:
    def __init__(self, job_fetcher, email_sender, user_settings):
        self.job_fetcher = job_fetcher
        self.email_sender = email_sender
        self.user_settings = user_settings
        self.thread = None
        self.running = False
    
    def start(self):
        if self.running:
            self.stop()
            
        self.running = True
        schedule.clear()
        
        notification_settings = self.user_settings.get_notification_settings()
        for time in notification_settings['times']:
            try:
                # 시간 형식이 올바른지 확인
                datetime.strptime(time, "%H:%M")
                schedule.every().day.at(time).do(self.check_and_send_alerts)
            except ValueError as e:
                logging.error(f"Invalid time format: {time}")
                st.error(f"잘못된 시간 형식입니다: {time}")
        
        self.thread = threading.Thread(target=self._run_schedule, daemon=True)
        self.thread.start()
    
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        schedule.clear()
    
    def restart(self):
        self.stop()
        self.start()
    
    def _run_schedule(self):
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def check_and_send_alerts(self):
        try:
            jobs = self.job_fetcher.fetch_all_jobs(
                keywords=self.user_settings.get_keywords()
            )
            
            if jobs:
                self.email_sender.send_job_alerts(
                    jobs,
                    {
                        'sender_email': self.user_settings.get_email_settings()['sender_email'],
                        'sender_password': self.user_settings.get_email_settings()['sender_password'],
                        'receivers': self.user_settings.get_receivers()
                    }
                )
                
            logging.info(f"Job check completed. Found {len(jobs)} matching jobs.")
            
        except Exception as e:
            logging.error(f"Error in scheduled job: {e}")
