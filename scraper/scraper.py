import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, BrowserContext, Page, PlaywrightTimeoutError

from dotenv import load_dotenv
from models import Lead, ScrapeJob, ScrapeResult, Platform, ScrapeStatus

# Load environment variables
load_dotenv()

# Configuration
SOCLEADS_BASE_URL = os.getenv("SOCLEADS_BASE_URL", "https://app.socleads.com")
SOCLEADS_EMAIL = os.getenv("SOCLEADS_EMAIL")
SOCLEADS_PASSWORD = os.getenv("SOCLEADS_PASSWORD")
ENABLED_PLATFORMS = [p.strip() for p in os.getenv("ENABLED_PLATFORMS", "ig_keyword,fb_keyword,tiktok_keyword").split(",")]
KEYWORDS = [k.strip() for k in os.getenv("KEYWORDS", "nike,adidas,reebok").split(",")]
MAX_CREDITS = int(os.getenv("MAX_CREDITS", "100"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "scraper/output"))


class SocLeadsScraper:
    def __init__(self):
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.browser: Optional[async_playwright] = None
        self.jobs: List[ScrapeJob] = []
        self.total_credits_used = 0
        self.running = False
        
    def log_message(self, level: str, module: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{module}] {message}")
    
    async def setup_directories(self):
        """Create required directories if they don't exist."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    async def login(self) -> bool:
        """Login to SocLeads with up to 3 retry attempts."""
        self.log_message("INFO", "scraper", "Starting login...")
        
        if not self.browser:
            self.browser = await async_playwright().start()
            self.context = await self.browser.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            self.context = await self.browser.chromium.new_context()
            self.page = await self.context.new_page()
            
            try:
                attempt_count = 0
                max_attempts = 3
                
                while attempt_count < max_attempts:
                    attempt_count += 1
                    
                    # Guard: Check if credentials are empty or None
                    if not SOCLEADS_EMAIL or not SOCLEADS_PASSWORD:
                        self.log_message("WARN", "scraper", f"Credentials missing (email: {SOCLEADS_EMAIL}, password: {SOCLEADS_PASSWORD})")
                        return False
                    
                    self.log_message("INFO", "scraper", f"Login attempt {attempt_count} of {max_attempts}")
                    
                    try:
                        await self.page.goto(SOCLEADS_BASE_URL, timeout=30000)
                        
                        # Wait for login form
                        await self.page.wait_for_selector('input[type="email"]', timeout=5000)
                        
                        # Fill credentials
                        email_input = self.page.locator('input[type="email"]')
                        password_input = self.page.locator('input[type="password"]')
                        
                        await email_input.fill(SOCLEADS_EMAIL)
                        await password_input.fill(SOCLEADS_PASSWORD)
                        
                        # Find and click login button
                        login_button = self.page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Ingresar")')
                        await login_button.click()
                        
                        # Wait for successful login
                        await self.page.wait_for_timeout(2000)
                        
                        # Check if logged in
                        is_logged_in = await self.page.wait_for_selector(
                            'div:has-text("Dashboard"), div:has-text("Scraper"), div:has-text("History")',
                            timeout=5000
                        )
                        
                        if is_logged_in:
                            self.log_message("INFO", "scraper", "Login successful!")
                            return True
                        else:
                            self.log_message("WARN", "scraper", "Login might not be successful")
                            continue
                    
                    except PlaywrightTimeoutError:
                        self.log_message("WARN", "scraper", f"Login timeout on attempt {attempt_count}, retrying...")
                        attempt_count += 1
                        
                        if attempt_count < max_attempts:
                            await asyncio.sleep(2)
                        else:
                            self.log_message("ERROR", "scraper", "Max login attempts reached")
                            return False
                    except Exception as e:
                        self.log_message("ERROR", "scraper", f"Login error on attempt {attempt_count}: {e}")
                        attempt_count += 1
                        
                        if attempt_count < max_attempts:
                            await asyncio.sleep(2)
                        else:
                            self.log_message("ERROR", "scraper", "Max login attempts reached")
                            return False
            finally:
                if self.browser:
                    await self.browser.stop()
        
        return False
    
    async def create_job(self, platform: Platform, keyword: str) -> ScrapeJob:
        """Create a new scrape job."""
        job_id = f"{platform.value}_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job = ScrapeJob(
            id=job_id,
            platform=platform,
            keyword=keyword,
            status=ScrapeStatus.PENDING
        )
        self.jobs.append(job)
        self.log_message("INFO", "scraper", f"Created job: {job_id}")
        return job
    
    async def run_scrape_job(self, job: ScrapeJob) -> bool:
        """Run a single scrape job."""
        self.log_message("INFO", "scraper", f"Starting job: {job.id}")
        
        job.status = ScrapeStatus.RUNNING
        job.started_at = datetime.now()
        
        try:
            # Navigate to scraper section
            await self.page.goto(f"{SOCLEADS_BASE_URL}/scraper", timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Ensure browser is still running
            if not self.browser:
                self.browser = await async_playwright().start()
                self.context = await self.browser.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                self.context = await self.browser.chromium.new_context()
                self.page = await self.context.new_page()
            
            # Wait for results
            max_wait = 120  # 120 seconds
            elapsed = 0
            
            while elapsed < max_wait:
                await self.page.wait_for_timeout(5000)  # Poll every 5s
                elapsed += 5
                
                # Check job status (polling)
                status = await self._check_job_status(job)
                
                if status == ScrapeStatus.COMPLETED:
                    job.status = ScrapeStatus.COMPLETED
                    job.completed_at = datetime.now()
                    self.log_message("INFO", "scraper", f"Job completed: {job.id}")
                    return True
                elif status == ScrapeStatus.FAILED:
                    job.status = ScrapeStatus.FAILED
                    job.completed_at = datetime.now()
                    self.log_message("ERROR", "scraper", f"Job failed: {job.id}")
                    return False
                
                # Check credits
                if self.total_credits_used >= MAX_CREDITS:
                    job.status = ScrapeStatus.CANCELLED
                    job.completed_at = datetime.now()
                    self.log_message("WARN", "scraper", f"Max credits reached, cancelling: {job.id}")
                    return True
            
            # Timeout
            job.status = ScrapeStatus.FAILED
            job.completed_at = datetime.now()
            job.error = "Timeout after 120s"
            self.log_message("WARN", "scraper", f"Job timed out: {job.id}")
            return False
            
        except PlaywrightTimeoutError:
            job.status = ScrapeStatus.FAILED
            job.completed_at = datetime.now()
            job.error = "Playwright timeout"
            self.log_message("WARN", "scraper", f"Job timeout: {job.id}")
            return True
        except Exception as e:
            job.status = ScrapeStatus.FAILED
            job.completed_at = datetime.now()
            job.error = str(e)
            self.log_message("ERROR", "scraper", f"Job error: {e}")
            return False
        
        finally:
            if self.browser:
                await self.browser.stop()
    
    async def _check_job_status(self, job: ScrapeJob) -> ScrapeStatus:
        """Check the status of a job by polling."""
        try:
            # Look for status indicators on the page
            status_text = await self.page.wait_for_timeout(1000)
            
            # Check for common status indicators
            status_elements = await self.page.query_selector_all(
                'div:has-text("Completed"), div:has-text("Running"), div:has-text("Pending"), div:has-text("Failed")'
            )
            
            if status_elements:
                for element in status_elements:
                    text = await element.text_content()
                    if "Completed" in text:
                        return ScrapeStatus.COMPLETED
                    elif "Running" in text:
                        return ScrapeStatus.RUNNING
                    elif "Pending" in text:
                        return ScrapeStatus.PENDING
                    elif "Failed" in text:
                        return ScrapeStatus.FAILED
            
            return ScrapeStatus.RUNNING
            
        except PlaywrightTimeoutError:
            self.log_message("WARN", "scraper", f"Status check timeout: {job.id}")
            return ScrapeStatus.RUNNING
        except Exception:
            return ScrapeStatus.RUNNING
    
    async def run_all_jobs(self) -> ScrapeResult:
        """Run all configured jobs."""
        self.log_message("INFO", "scraper", "=== Starting all scrape jobs ===")
        self.log_message("INFO", "scraper", f"Platforms: {ENABLED_PLATFORMS}")
        self.log_message("INFO", "scraper", f"Keywords: {KEYWORDS}")
        self.log_message("INFO", "scraper", f"Max credits: {MAX_CREDITS}")
        
        # Setup
        await self.setup_directories()
        
        # Login
        if not await self.login():
            self.log_message("WARN", "scraper", "Login failed, trying again...")
            await self.login()
        
        # Create and run jobs
        for platform in ENABLED_PLATFORMS:
            platform_obj = Platform(platform)
            
            # Skip platforms that pay per row without email
            if platform_obj in [Platform.GOOGLE_MAPS, Platform.IG_FOLLOWERS]:
                self.log_message("INFO", "scraper", f"Skipping {platform} (pay per row without email)")
                continue
            
            for keyword in KEYWORDS:
                # Check credits before starting
                if self.total_credits_used >= MAX_CREDITS:
                    self.log_message("WARN", "scraper", "Max credits reached, stopping jobs")
                    break
                
                job = await self.create_job(platform_obj, keyword)
                await self.run_scrape_job(job)
                
                # Update total credits
                self.total_credits_used = job.credits_used
        
        # Create result
        result = ScrapeResult(
            jobs=self.jobs,
            total_credits_used=self.total_credits_used,
            total_leads=sum(len(job.leads) for job in self.jobs),
            success_rate=len([j for j in self.jobs if j.status == ScrapeStatus.COMPLETED]) / len(self.jobs) if self.jobs else 0
        )
        
        # Save results
        await self._save_results(result)
        
        # Cleanup browser
        if self.browser:
            await self.browser.stop()
        
        self.log_message("INFO", "scraper", "=== All jobs completed ===")
        return result
    
    async def _save_results(self, result: ScrapeResult):
        """Save results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUT_DIR / f"leads_{timestamp}.json"
        
        data = {
            "timestamp": result.timestamp.isoformat(),
            "total_credits_used": result.total_credits_used,
            "total_leads": result.total_leads,
            "success_rate": result.success_rate,
            "jobs": [
                {
                    "id": job.id,
                    "platform": job.platform.value,
                    "keyword": job.keyword,
                    "status": job.status.value,
                    "credits_used": job.credits_used,
                    "leads_count": len(job.leads),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "error": job.error
                }
                for job in result.jobs
            ],
            "leads": [
                {
                    "platform": lead.platform.value,
                    "keyword": lead.keyword,
                    "email": lead.email,
                    "name": lead.name,
                    "link": lead.link,
                    "phone": lead.phone
                }
                for job in result.jobs
                for lead in job.leads
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.log_message("INFO", "scraper", f"Results saved to: {output_file}")


async def main():
    """Main function to run the scraper."""
    scraper = SocLeadsScraper()
    result = await scraper.run_all_jobs()
    
    # Print summary
    print("\n" + "="*80)
    print("SCRAPER SUMMARY")
    print("="*80)
    print(f"Total Jobs: {len(result.jobs)}")
    print(f"Total Leads: {result.total_leads}")
    print(f"Total Credits Used: {result.total_credits_used}")
    print(f"Success Rate: {result.success_rate*100:.1f}%")
    print(f"Output File: {OUTPUT_DIR}/leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
