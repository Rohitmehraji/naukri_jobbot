"""
Job scraper for Naukri.com using requests and BeautifulSoup.
Extracts job listings from search results.
"""
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

# Initialize user agent generator
ua = UserAgent()


def scrape_jobs(query: str, location: str, pages: int = 2) -> List[Dict]:
    """
    Scrape jobs from Naukri.com for given query and location.
    
    Args:
        query: Job search query (e.g., "Python Developer")
        location: Job location filter
        pages: Number of pages to scrape (default 2)
    
    Returns:
        List of job dictionaries with keys:
        - job_id: Unique job identifier
        - title: Job title
        - company: Company name
        - url: Job URL
        - description: Job description snippet
    """
    jobs = []
    
    try:
        for page in range(1, pages + 1):
            try:
                # Build search URL
                query_formatted = query.replace(" ", "-").lower()
                location_formatted = location.replace(" ", "-").lower()
                url = f"https://www.naukri.com/{query_formatted}-jobs-in-{location_formatted}"
                
                if page > 1:
                    url += f"?pageNo={page}"
                
                logger.info(f"Scraping page {page}: {url}")
                
                # Random delay to avoid detection
                time.sleep(1 + (page - 1) * 0.5)
                
                # Make request with random user agent
                headers = {
                    "User-Agent": ua.random,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.naukri.com/",
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Find job listings
                job_cards = soup.find_all("article", class_="jobTuple")
                
                if not job_cards:
                    logger.warning(f"No jobs found on page {page}")
                    continue
                
                logger.info(f"Found {len(job_cards)} jobs on page {page}")
                
                # Extract job information
                for card in job_cards:
                    try:
                        # Extract job title
                        title_elem = card.find("a", class_="jobCardTuple")
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        job_url = title_elem.get("href", "")
                        
                        # Extract job ID from URL
                        job_id = job_url.split("-")[-1] if job_url else ""
                        
                        # Extract company name
                        company_elem = card.find("p", class_="companyName")
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                        
                        # Extract job description/snippet
                        desc_elem = card.find("p", class_="jobDescription")
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        # Extract location from card
                        location_elem = card.find("p", class_="locWc")
                        job_location = location_elem.get_text(strip=True) if location_elem else ""
                        
                        job = {
                            "job_id": job_id,
                            "title": title,
                            "company": company,
                            "url": job_url,
                            "description": description,
                            "location": job_location,
                            "score": 0,
                            "reason": "",
                        }
                        
                        jobs.append(job)
                        logger.debug(f"Scraped: {title} at {company}")
                    
                    except Exception as e:
                        logger.warning(f"Error parsing job card: {str(e)}")
                        continue
            
            except requests.RequestException as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error processing page {page}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Fatal error in scrape_jobs: {str(e)}")
    
    logger.info(f"Total jobs scraped: {len(jobs)}")
    return jobs


def deduplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    Remove duplicate jobs based on job_id.
    
    Args:
        jobs: List of job dictionaries
    
    Returns:
        Deduplicated list of jobs
    """
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        if job["job_id"] not in seen:
            seen.add(job["job_id"])
            unique_jobs.append(job)
    
    logger.info(f"Deduplicated: {len(jobs)} -> {len(unique_jobs)} jobs")
    return unique_jobs
