"""
Job scraper for Naukri.com using requests and BeautifulSoup.
Extracts job listings from search results.
Updated to work with current Naukri.com HTML structure.
"""
import logging
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from fake_useragent import UserAgent
import json

logger = logging.getLogger(__name__)

# Initialize user agent generator
ua = UserAgent()


def scrape_jobs(query: str, location: str, pages: int = 2) -> List[Dict]:
    """
    Scrape jobs from Naukri.com for given query and location.
    Updated to use current Naukri.com API and structure.
    
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
        for page in range(pages):
            try:
                # Use Naukri's API endpoint for better reliability
                # API format: /gateway/v5/jobs/search
                query_formatted = query.replace(" ", "%20")
                location_formatted = location.replace(" ", "%20")
                
                # Build API request URL (more reliable than HTML scraping)
                url = f"https://www.naukri.com/gateway/v5/jobs/search"
                
                logger.info(f"Scraping page {page + 1}: {query} in {location}")
                
                # Random delay to avoid detection
                time.sleep(1 + page * 0.5)
                
                # Headers to mimic browser
                headers = {
                    "User-Agent": ua.random,
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.naukri.com/",
                    "X-Requested-With": "XMLHttpRequest",
                }
                
                # Query parameters
                params = {
                    "keyword": query,
                    "location": location,
                    "pageNo": page + 1,
                    "noOfResults": 20,
                    "sort": "newestFirst",
                    "experience": 0,
                    "salary": "",
                    "jobType": "",
                    "workMode": "",
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                
                try:
                    data = response.json()
                except:
                    # If JSON parsing fails, try HTML parsing as fallback
                    logger.warning(f"API response not JSON, trying HTML parse")
                    jobs.extend(_parse_html(response.text, page + 1))
                    continue
                
                # Extract jobs from API response
                if "jobDetails" in data:
                    job_details = data.get("jobDetails", [])
                    
                    if not job_details:
                        logger.warning(f"No jobs found on page {page + 1}")
                        continue
                    
                    logger.info(f"Found {len(job_details)} jobs on page {page + 1}")
                    
                    for job_item in job_details:
                        try:
                            job_id = job_item.get("jobId", "")
                            title = job_item.get("jobTitle", "")
                            company = job_item.get("companyName", "")
                            url = f"https://www.naukri.com/job-listings-{title.replace(' ', '-')}-{company.replace(' ', '-')}-{job_id}"
                            
                            # Try to get description from job item
                            description = job_item.get("jobDescription", "")
                            if not description:
                                description = job_item.get("jobCategory", "")
                            
                            job_location = job_item.get("location", "")
                            
                            job = {
                                "job_id": job_id,
                                "title": title,
                                "company": company,
                                "url": url,
                                "description": description,
                                "location": job_location,
                                "score": 0,
                                "reason": "",
                            }
                            
                            jobs.append(job)
                            logger.debug(f"Scraped: {title} at {company}")
                        
                        except Exception as e:
                            logger.debug(f"Error parsing job item: {str(e)}")
                            continue
                else:
                    logger.warning(f"Unexpected API response format on page {page + 1}")
            
            except requests.RequestException as e:
                logger.error(f"Error fetching page {page + 1}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error processing page {page + 1}: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Fatal error in scrape_jobs: {str(e)}")
    
    logger.info(f"Total jobs scraped: {len(jobs)}")
    return jobs


def _parse_html(html: str, page: int) -> List[Dict]:
    """
    Fallback HTML parsing if API fails.
    
    Args:
        html: HTML content
        page: Page number
    
    Returns:
        List of jobs found in HTML
    """
    jobs = []
    
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Try multiple CSS selectors for job cards
        job_selectors = [
            "article.jobTuple",
            "article[class*='jobTuple']",
            "div[class*='jobCard']",
            "div[data-job-id]",
            "a.jobCard",
        ]
        
        job_cards = []
        for selector in job_selectors:
            job_cards = soup.select(selector)
            if job_cards:
                logger.debug(f"Found {len(job_cards)} jobs using selector: {selector}")
                break
        
        if not job_cards:
            logger.warning(f"No job cards found using any selector on page {page}")
            return jobs
        
        for card in job_cards:
            try:
                # Extract job title
                title_elem = card.find("a", class_="jobCardTuple") or card.find("a")
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                job_url = title_elem.get("href", "")
                
                # Extract job ID from URL or data attribute
                job_id = card.get("data-job-id", job_url.split("-")[-1] if job_url else "")
                
                # Extract company name
                company_elem = card.find("p", class_="companyName") or card.find(class_=lambda x: x and "company" in x.lower())
                company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                
                # Extract job description
                desc_elem = card.find("p", class_="jobDescription") or card.find(class_=lambda x: x and "description" in x.lower())
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract location
                location_elem = card.find("p", class_="locWc") or card.find(class_=lambda x: x and "location" in x.lower())
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                job = {
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "url": job_url,
                    "description": description,
                    "location": location,
                    "score": 0,
                    "reason": "",
                }
                
                jobs.append(job)
                logger.debug(f"HTML Parsed: {title} at {company}")
            
            except Exception as e:
                logger.debug(f"Error parsing job card: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"Error in HTML parsing: {str(e)}")
    
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
        job_id = job.get("job_id", "")
        if job_id and job_id not in seen:
            seen.add(job_id)
            unique_jobs.append(job)
        elif not job_id:
            # Include jobs without ID
            unique_jobs.append(job)
    
    logger.info(f"Deduplicated: {len(jobs)} -> {len(unique_jobs)} jobs")
    return unique_jobs
