import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from google_sheets_helper import get_company_settings, get_keywords

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
                jobs = self._fetch_jobs_by_samsung(domain)
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

    def _fetch_jobs_by_samsung(self, domain):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)

        jobs = []
        try:
            driver.get(domain)
            time.sleep(3)
            job_elements = driver.find_elements(By.CSS_SELECTOR, 'li[onclick^="fn_view"]')
            for el in job_elements:
                onclick = el.get_attribute("onclick")
                if not onclick or "fn_view" not in onclick:
                    continue

                no = onclick.split("fn_view(")[1].split(")")[0]
                url = f"https://www.samsungcareers.com/hr/?no={no}"
                title = el.find_element(By.CLASS_NAME, "title").text.strip()
                dept = el.find_element(By.CLASS_NAME, "dept").text.strip()
                try:
                    desc = el.find_element(By.CLASS_NAME, "summary").text.strip()
                except:
                    desc = ""

                job = {
                    "title": f"{title} - {dept}",
                    "description": desc,
                    "link": url,
                    "career": "경력무관",
                    "deadline": "상시채용"
                }
                jobs.append(job)
        except Exception as e:
            print(f"셀레니움 오류: {e}")
        finally:
            driver.quit()

        return jobs

    def _filter_jobs(self, jobs, keywords, career_filter):
        return [
            job for job in jobs
            if any(keyword.lower() in (job['title'] + job['description']).lower() for keyword in keywords)
            and (not career_filter or job.get('career', '경력무관') in career_filter)
        ]
