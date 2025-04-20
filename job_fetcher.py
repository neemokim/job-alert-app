import requests
from bs4 import BeautifulSoup
from google_sheets_helper import get_company_settings, get_keywords
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
import time

class JobFetcher:
    def __init__(self):
        self.company_info = get_company_settings()
        self.keywords = get_keywords()

    def fetch_all_jobs(self, keywords=None, career_filter=None):
        if keywords is None:
            keywords = self.keywords
        if career_filter is None:
            career_filter = ["경력", "신입/경력", "경력무관"]

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
                if "samsung" in domain:
                    jobs = self._fetch_samsung_jobs(domain)
                elif "naver" in domain:
                    jobs = self._fetch_naver_jobs(domain)
                elif "google" in domain:
                    jobs = self._fetch_google_jobs(domain)
                else:
                    jobs = self._fetch_jobs_by_selenium(domain)
            else:
                jobs = []

            filtered = self._filter_jobs(jobs, keywords, career_filter)
            for job in filtered:
                job["company"] = name
            results.extend(filtered)

        return results

    def _setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        chromedriver_autoinstaller.install()
        return webdriver.Chrome(options=options)

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
        return []

    def _fetch_samsung_jobs(self, domain):
        driver = self._setup_driver()
        jobs = []
        try:
            driver.get(domain)
            time.sleep(5)
            job_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.recruit-list li')
            for elem in job_elements:
                try:
                    title = elem.find_element(By.CSS_SELECTOR, 'strong').text.strip()
                    link = elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    deadline = elem.find_element(By.CSS_SELECTOR, '.close-day').text.strip()
                    company_name = elem.find_element(By.CSS_SELECTOR, '.company').text.strip() if elem.find_elements(By.CSS_SELECTOR, '.company') else "삼성"

                    if link and not link.startswith("http"):
                        link = "https://www.samsungcareers.com" + link

                    jobs.append({
                        "title": title,
                        "description": title,
                        "link": link,
                        "career": "경력무관",
                        "deadline": deadline if deadline else "상시채용",
                        "company": company_name
                    })
                except:
                    continue
        except Exception as e:
            print("삼성 셀레니움 오류:", e)
        finally:
            driver.quit()
        return jobs

    def _fetch_naver_jobs(self, domain):
        driver = self._setup_driver()
        jobs = []
        try:
            driver.get(domain)
            time.sleep(5)
            job_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.list_job li')
            for elem in job_elements:
                try:
                    title = elem.find_element(By.CSS_SELECTOR, 'strong.tit').text.strip()
                    link = elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    deadline = elem.find_element(By.CSS_SELECTOR, '.date').text.strip()

                    jobs.append({
                        "title": title,
                        "description": title,
                        "link": link,
                        "career": "경력무관",
                        "deadline": deadline if deadline else "상시채용"
                    })
                except:
                    continue
        except Exception as e:
            print("네이버 셀레니움 오류:", e)
        finally:
            driver.quit()
        return jobs

    def _fetch_google_jobs(self, domain):
        driver = self._setup_driver()
        jobs = []
        try:
            driver.get(domain)
            time.sleep(5)
            job_elements = driver.find_elements(By.CSS_SELECTOR, 'ul.JobsList li')
            for elem in job_elements:
                try:
                    title = elem.find_element(By.TAG_NAME, 'a').text.strip()
                    link = elem.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    jobs.append({
                        "title": title,
                        "description": title,
                        "link": link,
                        "career": "경력무관",
                        "deadline": "상시채용"
                    })
                except:
                    continue
        except Exception as e:
            print("구글 셀레니움 오류:", e)
        finally:
            driver.quit()
        return jobs

    def _filter_jobs(self, jobs, keywords, career_filter):
        return [
            job for job in jobs
            if (
                any(keyword.lower() in (job['title'] + job['description']).lower() for keyword in keywords)
                and job.get('career', '경력무관') in career_filter
            )
        ]
