import requests
from bs4 import BeautifulSoup
from google_sheets_helper import get_company_settings, get_keywords
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class JobFetcher:
    def __init__(self):
        self.company_info = get_company_settings()
        self.keywords = get_keywords()

    def fetch_all_jobs(self, keywords=None):
        if keywords is None:
            keywords = self.keywords

        results = []
        for company in self.company_info:
            domain = company.get("크롤링 URL 도메인")
            method = company.get("크롤링 방식", "requests").lower()
            if not domain:
                continue
            name = company.get("회사명", "")

            if method == "requests":
                jobs = self._fetch_jobs_by_requests(domain)
            elif method == "selenium":
                jobs = self._fetch_jobs_by_selenium(domain)
            else:
                jobs = []

            filtered = self._filter_jobs(jobs, keywords)
            for job in filtered:
                job["company"] = name
            results.extend(filtered)

        return results

    def _fetch_jobs_by_requests(self, domain):
        try:
            res = requests.get(domain, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")
            jobs = []
            for a in links:
                title = a.get_text(strip=True)
                href = a.get("href")
                if not title or not href:
                    continue
                jobs.append({
                    "title": title,
                    "description": title,
                    "link": href if href.startswith("http") else domain.rstrip("/") + href,
                    "career": "경력무관",
                    "deadline": "상시채용"
                })
            return jobs
        except:
            return []

    def _fetch_jobs_by_selenium(self, domain):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        jobs = []

        try:
            driver.get(domain)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)

            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    title = link.text.strip()
                    href = link.get_attribute("href")
                    if not title or not href:
                        continue
                    jobs.append({
                        "title": title,
                        "description": title,
                        "link": href,
                        "career": "경력무관",
                        "deadline": "상시채용"
                    })
                except:
                    continue
        except:
            pass
        finally:
            driver.quit()

        return jobs

    def _filter_jobs(self, jobs, keywords):
        return [
            job for job in jobs
            if any(keyword.lower() in (job['title'] + job['description']).lower() for keyword in keywords)
        ]
