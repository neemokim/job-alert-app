from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st  # streamlit import 추가
import logging
from datetime import datetime

class JobFetcher:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        
        try:
            service = Service()
            self.driver = webdriver.Chrome(
                options=chrome_options
            )
        except Exception as e:
            logging.error(f"Chrome driver initialization failed: {e}")
            # 에러 메시지 변경
            logging.error(str(e))
            self.driver = None
        
        self.companies = {
            "네이버": {
                "url": "https://careers.naver.com/jobs/list/developer",
                "logo": "https://www.naver.com/favicon.ico"
            },
            "네이버파이낸셜": {
                "url": "https://careers.naverfincorp.com/jobs/list/developer",
                "logo": "https://naverfincorp.com/favicon.ico"
            },
            "삼성전자": {
                "url": "https://careers.samsung.com/jobs",
                "logo": "https://www.samsung.com/favicon.ico"
            },
            "구글코리아": {
                "url": "https://careers.google.com/jobs/results/?location=Korea",
                "logo": "https://www.google.com/favicon.ico"
            },
            "SKT": {
                "url": "https://careers.sktelecom.com/jobs",
                "logo": "https://www.sktelecom.com/favicon.ico"
            }
        }
    
    def fetch_all_jobs(self, keywords=None):
        if self.driver is None:
            st.warning("브라우저 초기화에 실패했습니다. 채용 정보를 가져올 수 없습니다.")
            return []
            
        all_jobs = []
        try:
            for company, info in self.companies.items():
                jobs = self._fetch_company_jobs(company, info["url"], info["logo"], keywords)
                all_jobs.extend(jobs)
        finally:
            if self.driver:
                self.driver.quit()
        return all_jobs
    
    def _fetch_company_jobs(self, company, url, logo_url, keywords):
        jobs = []
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            if "naver" in url:
                jobs = self._fetch_naver_jobs(company, logo_url)
            elif "samsung" in url:
                jobs = self._fetch_samsung_jobs(company, logo_url)
            elif "google" in url:
                jobs = self._fetch_google_jobs(company, logo_url)
            elif "skt" in url:
                jobs = self._fetch_skt_jobs(company, logo_url)
                
            if keywords:
                jobs = [job for job in jobs if any(
                    keyword.lower() in job['title'].lower() or 
                    keyword.lower() in job['description'].lower() 
                    for keyword in keywords
                )]
                
        except Exception as e:
            logging.error(f"Error fetching {company} jobs: {e}")
            
        return jobs
    
    def _fetch_naver_jobs(self, company, logo_url):
        jobs = []
        try:
            job_cards = self.driver.find_elements(By.CLASS_NAME, "card-list-item")
            for card in job_cards:
                try:
                    title = card.find_element(By.CLASS_NAME, "card-title").text
                    description = card.find_element(By.CLASS_NAME, "card-description").text
                    link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    career = card.find_element(By.CLASS_NAME, "career-type").text
                    deadline = card.find_element(By.CLASS_NAME, "deadline").text
                    
                    jobs.append({
                        "company": company,
                        "company_logo": logo_url,
                        "title": title,
                        "description": description,
                        "link": link,
                        "career": career,
                        "deadline": deadline,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                except Exception as e:
                    logging.error(f"Error parsing {company} job card: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error fetching {company} jobs: {e}")
        return jobs
    
    def _fetch_samsung_jobs(self, company, logo_url):
        # Samsung 채용 페이지 크롤링 로직
        return []
    
    def _fetch_google_jobs(self, company, logo_url):
        # Google 채용 페이지 크롤링 로직
        return []
    
    def _fetch_skt_jobs(self, company, logo_url):
        # SKT 채용 페이지 크롤링 로직
        return []
