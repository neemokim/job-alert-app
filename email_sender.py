import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import yagmail


class EmailSender:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    def send_email(self, receiver_email, jobs):
        email_settings = {
            "sender_email": st.secrets["SENDER_EMAIL"],
            "sender_password": st.secrets["SENDER_PASSWORD"],
            "receivers": [{"이메일 주소": receiver_email, "활성화": True}]
        }
        self.send_job_alerts(jobs, email_settings)

    
    def send_job_alerts(self, jobs, email_settings):
        if not jobs:
            return
            
        try:
            for receiver in email_settings['receivers']:
                if not receiver['활성화']:
                    continue
                    
                message = self._create_email_message(
                    jobs, 
                    email_settings['sender_email'],
                    receiver['이메일 주소']
                )
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(
                        email_settings['sender_email'],
                        email_settings['sender_password']
                    )
                    server.send_message(message)
                    
                logging.info(f"Successfully sent job alerts to {receiver['이메일 주소']}")
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
    
    def _create_email_message(self, jobs, sender_email, receiver_email):
        message = MIMEMultipart()
        message["Subject"] = f"새로운 채용 공고 알림 ({len(jobs)}건)"
        message["From"] = sender_email
        message["To"] = receiver_email
        
        html_content = self._create_html_content(jobs)
        message.attach(MIMEText(html_content, "html"))
        
        return message
    
       def _create_html_content(self, jobs):
        html = """
        <html>
            <head>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        line-height: 1.6;
                        padding: 10px;
                    }
                    .job-card {
                        margin-bottom: 25px;
                        border-bottom: 1px solid #eee;
                        padding-bottom: 15px;
                    }
                    .company {
                        font-size: 15px;
                        font-weight: bold;
                        color: #333;
                    }
                    .job-title {
                        font-size: 16px;
                        margin: 5px 0;
                        color: #222;
                    }
                    .deadline {
                        font-size: 14px;
                        color: #888;
                    }
                    a {
                        color: #1a73e8;
                        text-decoration: none;
                        font-weight: bold;
                    }
                    a:hover {
                        text-decoration: underline;
                    }
                </style>
            </head>
            <body>
                <h2>📣 신규 채용 공고 알림</h2>
        """
    
        for job in jobs:
            html += f"""
            <div class="job-card">
                <div class="company">📌 {job['company']}</div>
                <div class="job-title">"{job['title']} ({job.get('career', '경력무관')})"</div>
                <div class="deadline">🗓 마감일: {job.get('deadline', '상시채용')}</div>
                <div>🔗 <a href="{job['link']}" target="_blank">공고 바로가기</a></div>
            </div>
            """
    
        html += """
            </body>
        </html>
        """
        return html

