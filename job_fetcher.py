import requests
from bs4 import BeautifulSoup
from google_sheets_helper import get_company_settings, get_keywords
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class JobFetcher:
    def __init__(self):
        self.company_info = get_company_settings()
        self.keywords = get_keywords()

    def fetch_all_jobs(self, keywords=None, career_filter=None):
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

            filtered = self._filter_jobs(jobs, keywords, career_filter)
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
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)

        jobs = []
        try:
            driver.get(domain)
            time.sleep(3)

            if "samsungcareers" in domain:
                job_items = driver.find_elements(By.CSS_SELECTOR, ".recruit-list li")
                for item in job_items:
                    try:
                        link_elem = item.find_element(By.CSS_SELECTOR, "a")
                        link = link_elem.get_attribute("href")
                        title = item.find_element(By.CSS_SELECTOR, ".title").text.strip()
                        dept = item.find_element(By.CSS_SELECTOR, ".dept").text.strip()
                        deadline = item.find_element(By.CSS_SELECTOR, ".date span:last-child").text.strip()

                        jobs.append({
                            "title": f"{dept} - {title}",
                            "description": title,
                            "link": link,
                            "career": "경력무관",
                            "deadline": deadline if deadline else "상시채용"
                        })
                    except:
                        continue

        except Exception as e:
            print("셀레니움 오류:", e)
        finally:
            driver.quit()

        return jobs

    def _filter_jobs(self, jobs, keywords, career_filter):
        return [
            job for job in jobs
            if any(keyword.lower() in (job['title'] + job['description']).lower() for keyword in keywords)
            and (not career_filter or job.get('career', '경력무관') in career_filter)
        ]
