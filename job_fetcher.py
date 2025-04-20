import requests
from bs4 import BeautifulSoup
from google_sheets_helper import get_company_settings, get_keywords

class JobFetcher:
    def __init__(self):
        self.company_info = get_company_settings()  # ✅ 캐시된 회사 정보
        self.keywords = get_keywords()              # ✅ 캐시된 키워드

    def fetch_all_jobs(self, keywords=None, career_filter=None):
        if keywords is None:
            keywords = self.keywords
        if career_filter is None:
            career_filter = ["경력", "신입/경력", "경력무관"]  # 기본값

        results = []
        for company in self.company_info:
            domain = company.get("크롤링 URL 도메인")
            if not domain:
                continue
            company_name = company["회사명"]

            jobs = self._fetch_jobs_from_domain(domain)
            filtered = self._filter_jobs(jobs, keywords, career_filter)

            for job in filtered:
                job["company"] = company_name
            results.extend(filtered)

        return results

    def _fetch_jobs_from_domain(self, domain):
        try:
            res = requests.get(f"https://{domain}", timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a")
            jobs = []
            for a in links:
                title = a.get_text(strip=True)
                href = a.get("href")
                if not href or not title:
                    continue
                jobs.append({
                    "title": title,
                    "description": title,
                    "link": href if href.startswith("http") else f"https://{domain}{href}",
                    "career": "경력무관",
                    "deadline": "상시채용"
                })
            return jobs
        except:
            return []

    def _filter_jobs(self, jobs, keywords, career_filter):
        return [
            job for job in jobs
            if (
                any(keyword.lower() in (job['title'] + job['description']).lower() for keyword in keywords)
                and job.get('career', '경력무관') in career_filter
            )
        ]
