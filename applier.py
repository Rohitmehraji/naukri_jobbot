"""
Naukri.com job application automation using Playwright.
Handles login, job application, form filling, and resume upload.
"""
import asyncio
import json
import logging
import os
from typing import List, Dict
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logger = logging.getLogger(__name__)

COOKIES_FILE = "logs/cookies.json"
APPLIED_JOBS_FILE = "logs/applied_jobs.json"


class NaukriApplier:
    """Automates job applications on Naukri.com using Playwright."""
    
    def __init__(self, config: Dict):
        """
        Initialize the applier with configuration.
        
        Args:
            config: Configuration dictionary from config.py
        """
        self.config = config
        self.browser = None
        self.context = None
        self.applied_jobs = self._load_applied_jobs()
    
    def _load_applied_jobs(self) -> Dict:
        """
        Load previously applied jobs from file.
        
        Returns:
            Dictionary with job_id as key
        """
        try:
            if os.path.exists(APPLIED_JOBS_FILE):
                with open(APPLIED_JOBS_FILE, "r") as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} previously applied jobs")
                    return data
        except Exception as e:
            logger.warning(f"Could not load applied jobs: {str(e)}")
        
        return {}
    
    def _save_applied_jobs(self):
        """Save applied jobs to file."""
        try:
            os.makedirs("logs", exist_ok=True)
            with open(APPLIED_JOBS_FILE, "w") as f:
                json.dump(self.applied_jobs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving applied jobs: {str(e)}")
    
    def _is_already_applied(self, job_id: str) -> bool:
        """Check if job already applied."""
        return job_id in self.applied_jobs
    
    async def _save_cookies(self, context: BrowserContext):
        """Save browser cookies after login."""
        try:
            os.makedirs("logs", exist_ok=True)
            cookies = await context.cookies()
            with open(COOKIES_FILE, "w") as f:
                json.dump(cookies, f)
            logger.info("Cookies saved successfully")
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")
    
    async def _load_cookies(self, context: BrowserContext):
        """Load cookies to skip login."""
        try:
            if os.path.exists(COOKIES_FILE):
                with open(COOKIES_FILE, "r") as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)
                    logger.info("Cookies loaded successfully")
                    return True
        except Exception as e:
            logger.warning(f"Could not load cookies: {str(e)}")
        
        return False
    
    async def _login(self, page: Page) -> bool:
        """
        Login to Naukri.com.
        
        Args:
            page: Playwright page object
        
        Returns:
            True if login successful
        """
        try:
            logger.info("Attempting login to Naukri.com")
            
            # Navigate to Naukri
            await page.goto("https://www.naukri.com/", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Click login button
            try:
                login_button = page.locator("[class*='login'], [class*='Login'], a:has-text('Login')")
                await login_button.first.click(timeout=5000)
                await page.wait_for_timeout(1000)
            except:
                logger.warning("Could not find login button, checking if already logged in")
            
            # Fill email
            email_field = page.locator("input[type='email'], input[placeholder*='email'], input[placeholder*='Email']")
            await email_field.fill(self.config["email"], timeout=5000)
            logger.debug("Email filled")
            await page.wait_for_timeout(500)
            
            # Fill password
            password_field = page.locator("input[type='password']")
            await password_field.fill(self.config["password"], timeout=5000)
            logger.debug("Password filled")
            await page.wait_for_timeout(500)
            
            # Click submit
            submit_button = page.locator("button[type='submit'], button:has-text('Login'), button:has-text('Sign In')")
            await submit_button.first.click(timeout=5000)
            
            # Wait for login to complete (check for profile icon)
            try:
                await page.wait_for_selector("[class*='profileIcon'], [class*='userProfile']", timeout=15000)
                logger.info("✓ Login successful")
                return True
            except:
                logger.error("Login verification failed")
                return False
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    async def _apply_to_job(self, page: Page, job: Dict) -> bool:
        """
        Apply to a specific job.
        
        Args:
            page: Playwright page object
            job: Job dictionary with URL and details
        
        Returns:
            True if application successful
        """
        job_id = job.get("job_id", "unknown")
        job_title = job.get("title", "Unknown Job")
        
        try:
            # Check if already applied
            if self._is_already_applied(job_id):
                logger.info(f"⊘ Skipped (already applied): {job_title}")
                return False
            
            logger.info(f"→ Applying to: {job_title}")
            
            # Navigate to job
            job_url = job.get("url", "")
            if not job_url:
                logger.warning(f"  No URL for job {job_id}")
                return False
            
            await page.goto(job_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # Look for Apply button
            apply_button = None
            try:
                # Try to find Apply button (not "Applied")
                buttons = page.locator("button:has-text('Apply'), a:has-text('Apply')")
                count = await buttons.count()
                
                if count == 0:
                    logger.warning(f"  No Apply button found - may already be applied or not eligible")
                    return False
                
                # Find the first clickable apply button
                for i in range(count):
                    button = buttons.nth(i)
                    text = await button.text_content()
                    if "Applied" not in text:
                        apply_button = button
                        break
                
                if not apply_button:
                    logger.warning(f"  Already applied or unable to apply")
                    return False
            except:
                logger.warning(f"  Could not locate Apply button")
                return False
            
            # Click Apply
            await apply_button.click(timeout=5000)
            await page.wait_for_timeout(1500)
            
            # Handle application form steps
            # Step 1: Resume upload
            try:
                resume_input = page.locator("input[type='file']")
                if await resume_input.count() > 0:
                    resume_path = os.path.abspath(self.config["resume_path"])
                    if os.path.exists(resume_path):
                        await resume_input.set_input_files(resume_path)
                        logger.debug("  Resume uploaded")
                        await page.wait_for_timeout(1000)
                    else:
                        logger.warning(f"  Resume file not found: {resume_path}")
            except Exception as e:
                logger.debug(f"  Resume upload skipped: {str(e)}")
            
            # Step 2: Fill text fields if any
            try:
                text_inputs = page.locator("input[type='text'], textarea")
                count = await text_inputs.count()
                
                for i in range(min(count, 3)):  # Fill up to 3 fields
                    field = text_inputs.nth(i)
                    placeholder = await field.get_attribute("placeholder") or ""
                    
                    # Fill based on placeholder or position
                    if any(x in placeholder.lower() for x in ["name", "full name", "candidate"]):
                        await field.fill(self.config["candidate"]["name"])
                    elif any(x in placeholder.lower() for x in ["phone", "mobile", "contact"]):
                        await field.fill(self.config["candidate"]["phone"])
                    elif any(x in placeholder.lower() for x in ["skill", "experience"]):
                        await field.fill(self.config["candidate"]["skills"])
            except:
                logger.debug("  No text fields to fill")
            
            # Step 3: Click Next/Submit buttons
            submit_button = None
            try:
                # Look for submit button (Next, Submit, Continue, Apply, etc.)
                buttons = page.locator("button:has-text('Next'), button:has-text('Submit'), button:has-text('Continue'), button:has-text('Apply')")
                count = await buttons.count()
                
                if count > 0:
                    submit_button = buttons.first
            except:
                pass
            
            if submit_button:
                try:
                    await submit_button.click(timeout=5000)
                    await page.wait_for_timeout(2000)
                    logger.info(f"  ✓ Applied successfully")
                    
                    # Record applied job
                    self.applied_jobs[job_id] = {
                        "title": job_title,
                        "company": job.get("company", ""),
                        "url": job_url,
                        "timestamp": __import__('datetime').datetime.now().isoformat(),
                    }
                    self._save_applied_jobs()
                    
                    return True
                except:
                    logger.warning(f"  Submission may have failed")
                    return False
            else:
                logger.warning(f"  No submit button found")
                return False
        
        except Exception as e:
            logger.error(f"  Error applying: {str(e)}")
            return False
    
    async def run(self, jobs: List[Dict]):
        """
        Main runner: login and apply to jobs.
        
        Args:
            jobs: List of job dictionaries to apply to
        """
        async with async_playwright() as p:
            try:
                # Launch browser
                self.browser = await p.chromium.launch(headless=self.config["headless"])
                self.context = await self.browser.new_context()
                page = await self.context.new_page()
                
                # Try to load cookies (skip login if valid)
                cookies_loaded = await self._load_cookies(self.context)
                
                if not cookies_loaded:
                    # Perform login
                    if not await self._login(page):
                        logger.error("Login failed, aborting")
                        return
                    
                    # Save cookies after successful login
                    await self._save_cookies(self.context)
                else:
                    logger.info("Using cached login cookies")
                    # Verify cookies are still valid
                    await page.goto("https://www.naukri.com/")
                    await page.wait_for_timeout(1000)
                
                # Apply to jobs
                applied_count = 0
                skipped_count = 0
                
                for job in jobs:
                    # Add delay between applications
                    await page.wait_for_timeout(self.config["delay_seconds"] * 1000)
                    
                    result = await self._apply_to_job(page, job)
                    
                    if result:
                        applied_count += 1
                    else:
                        skipped_count += 1
                
                # Summary
                logger.info("="*60)
                logger.info(f"APPLICATIONS COMPLETED")
                logger.info(f"  Applied: {applied_count}")
                logger.info(f"  Skipped: {skipped_count}")
                logger.info(f"  Total: {len(jobs)}")
                logger.info("="*60)
            
            except Exception as e:
                logger.error(f"Fatal error in run: {str(e)}")
            
            finally:
                if self.browser:
                    await self.browser.close()
