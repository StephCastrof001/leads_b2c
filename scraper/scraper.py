import asyncio
import csv
import io
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, BrowserContext, Page, Playwright, TimeoutError as PlaywrightTimeoutError

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
        self.playwright: Optional[Playwright] = None
        self.jobs: List[ScrapeJob] = []
        self.total_credits_used = 0
        self.running = False
        self.traffic_data: List[Dict[str, Any]] = []
        self.traffic_job_id: Optional[str] = None
        
    def log_message(self, level: str, module: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] [{module}] {message}")
    
    async def setup_directories(self):
        """Create required directories if they don't exist."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    async def login(self) -> bool:
        """Login to SocLeads with up to 3 retry attempts."""
        self.log_message("INFO", "scraper", "Starting login...")
        
        if not self.playwright:
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                          '--disable-blink-features=AutomationControlled']
                )
                self.context = await self.browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                self.page = await self.context.new_page()
                await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
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
                            await self.page.goto(SOCLEADS_BASE_URL, timeout=30000, wait_until='domcontentloaded')
                            await self.page.wait_for_timeout(8000)
                            
                            # Wait for login form
                            await self.page.wait_for_selector('input[placeholder="Email"]', timeout=15000)
                            
                            # Fill credentials
                            email_input = self.page.locator('input[placeholder="Email"]')
                            password_input = self.page.locator('input[placeholder="Password"]')
                            
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
                            
                            if attempt_count < max_attempts:
                                await asyncio.sleep(2)
                            else:
                                self.log_message("ERROR", "scraper", "Max login attempts reached")
                                return False
                        except Exception as e:
                            self.log_message("ERROR", "scraper", f"Login error on attempt {attempt_count}: {e}")
                            
                            if attempt_count < max_attempts:
                                await asyncio.sleep(2)
                            else:
                                self.log_message("ERROR", "scraper", "Max login attempts reached")
                                return False
                except Exception:
                    pass
                
                return True
                
            except Exception:
                # Outer try-catch for browser setup
                if self.browser:
                    await self.browser.stop()
                return False
        
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
            # Start traffic capture
            await self._start_traffic_capture(job.id)
            
            # Navigate to the correct platform using sidebar link text
            platform_link = self._get_platform_link_text(job.platform)
            if not platform_link:
                job.status = ScrapeStatus.FAILED
                job.error = "Unknown platform"
                self.log_message("ERROR", "scraper", f"Unknown platform: {job.platform}")
                return False
            
            self.log_message("INFO", "scraper", f"Navigating to: {platform_link}")
            await self.page.click(f"text={platform_link}", timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Fill the "Enter keyword" input
            keyword_input = self.page.locator('input[placeholder="Enter keyword"]')
            await keyword_input.fill(job.keyword)
            
            # Fill the "How many results?" input with a number > 0
            results_input = self.page.locator('input[placeholder="How many results?"]')
            await results_input.fill("10")
            
            # Click the "Search" button
            search_button = self.page.locator('button:has-text("Search")')
            await search_button.click()
            
            self.log_message("INFO", "scraper", f"Job submitted: {job.id}")
            
            # Wait for results
            if await self.wait_for_job_completion(job):
                job.status = ScrapeStatus.COMPLETED
                job.completed_at = datetime.now()
                self.log_message("INFO", "scraper", f"Job completed: {job.id}")
            else:
                job.status = ScrapeStatus.FAILED
                job.completed_at = datetime.now()
                job.error = "Timeout after 300s"
                self.log_message("WARN", "scraper", f"Job timed out: {job.id}")
            
            # Download results if completed
            if job.status == ScrapeStatus.COMPLETED:
                await self.download_job_results(job)
            
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
        
        # Stop traffic capture
        await self._stop_traffic_capture()
        
        # Keep browser alive for subsequent jobs
        if self.running:
            return True
    
    async def _get_platform_link_text(self, platform: Platform) -> str:
        """Get the sidebar link text for a platform."""
        platform_links = {
            Platform.IG_KEYWORD: "Scrape Instagram Keyword",
            Platform.FB_KEYWORD: "Scrape Facebook",
            Platform.TIKTOK_KEYWORD: "Scrape TikTok keyword",
        }
        return platform_links.get(platform)
    
    async def wait_for_job_completion(self, job: ScrapeJob) -> bool:
        """Wait for job to complete in the 'Scraping results' table.
        
        Navigates to 'Scraping results' sidebar link, polls the table every 10 seconds,
        and returns True when a row containing the keyword has Status 'Completed'.
        Returns False if Status is 'Failed' or after 300 seconds timeout.
        """
        self.log_message("INFO", "scraper", f"Waiting for job completion: {job.id}")
        
        # Navigate to "Scraping results" via sidebar link
        platform_link = self._get_platform_link_text(job.platform)
        if not platform_link:
            self.log_message("ERROR", "scraper", f"Unknown platform: {job.platform}")
            return False
        
        self.log_message("INFO", "scraper", f"Navigating to: {platform_link}")
        await self.page.click(f"text={platform_link}", timeout=30000)
        await self.page.wait_for_load_state("networkidle", timeout=30000)
        
        # Poll the table every 10 seconds
        max_wait = 300  # 300 seconds
        elapsed = 0
        
        while elapsed < max_wait:
            await self.page.wait_for_timeout(10000)  # Poll every 10s
            elapsed += 10
            
            # Check job status by looking for the keyword row
            status = await self._check_job_row_status(job)
            
            if status == ScrapeStatus.COMPLETED:
                self.log_message("INFO", "scraper", f"Job completed in table: {job.id}")
                return True
            elif status == ScrapeStatus.FAILED:
                self.log_message("ERROR", "scraper", f"Job failed in table: {job.id}")
                return False
        
        self.log_message("WARN", "scraper", f"Job timeout after {max_wait}s: {job.id}")
        return False
    
    async def _check_job_row_status(self, job: ScrapeJob) -> ScrapeStatus:
        """Check the status of a specific job row in the table."""
        try:
            # Search for the keyword in the table
            keyword_selector = f"tr:has-text('{job.keyword}')"
            rows = await self.page.query_selector_all(keyword_selector)
            
            if not rows:
                self.log_message("WARN", "scraper", f"Keyword not found in table: {job.keyword}")
                return ScrapeStatus.RUNNING
            
            # Check the status column for this row
            for row in rows:
                # Get all cells in the row
                cells = await row.query_selector_all("td, th")
                if len(cells) >= 5:
                    # Check the Status column (typically 5th column)
                    status_cell = await cells[4].text_content()
                    
                    if "Completed" in status_cell:
                        return ScrapeStatus.COMPLETED
                    elif "Failed" in status_cell:
                        return ScrapeStatus.FAILED
                    elif "Running" in status_cell:
                        return ScrapeStatus.RUNNING
            
            return ScrapeStatus.RUNNING
            
        except PlaywrightTimeoutError:
            self.log_message("WARN", "scraper", f"Row status check timeout: {job.id}")
            return ScrapeStatus.RUNNING
        except Exception as e:
            self.log_message("ERROR", "scraper", f"Row status check error: {e}")
            return ScrapeStatus.RUNNING
    
    async def download_job_results(self, job: ScrapeJob) -> bool:
        """Download and parse the CSV results for a completed job.
        
        Clicks 'Export all CSV', parses the downloaded file, and populates job.leads.
        Returns True if successful, False otherwise.
        """
        self.log_message("INFO", "scraper", f"Downloading results for job: {job.id}")
        
        # Click "Export all CSV" button
        try:
            export_button = self.page.locator('button:has-text("Export all CSV")')
            await export_button.click()
            
            # Use Playwright's expect_download to capture the download event
            try:
                async with self.page.expect_download(timeout=10000) as download_info:
                    await self.page.wait_for_timeout(5000)
                
                download = await download_info.value
                file_path = await download.path()
            except PlaywrightTimeoutError:
                self.log_message("ERROR", "scraper", f"Download event timeout: {job.id}")
                raise
            
            self.log_message("INFO", "scraper", f"Downloaded file: {file_path}")
            
            # Parse the CSV file
            leads = await self._parse_csv_file(file_path, job)
            
            if leads:
                job.leads = leads
                job.credits_used = len(job.leads)
                self.log_message("INFO", "scraper", f"Downloaded {len(leads)} leads for job: {job.id}")
                return True
            else:
                self.log_message("WARN", "scraper", f"CSV downloaded but no leads found for job: {job.id}")
                job.leads = []
                return True
                
        except PlaywrightTimeoutError:
            self.log_message("ERROR", "scraper", f"Download timeout: {job.id}")
            return False
        except Exception as e:
            self.log_message("ERROR", "scraper", f"Download error: {e}")
            return False
    
    async def _parse_csv_file(self, file_path: str, job: ScrapeJob) -> List[Lead]:
        """Parse the downloaded CSV file and return Lead objects."""
        leads = []
        
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse CSV
            reader = csv.DictReader(io.StringIO(content))
            
            for row in reader:
                # Extract fields (based on expected CSV columns)
                email = row.get('email', '').strip()
                name = row.get('name', row.get('full_name', '')).strip()
                link = row.get('link', row.get('profile_url', '')).strip()
                
                # Only add if email is present
                if email:
                    lead = Lead(
                        platform=job.platform,
                        keyword=job.keyword,
                        email=email,
                        name=name,
                        link=link,
                        phone=''  # May be empty if not in CSV
                    )
                    leads.append(lead)
            
            return leads
            
        except Exception as e:
            self.log_message("ERROR", "scraper", f"CSV parse error: {e}")
            return leads
    
    async def _start_traffic_capture(self, job_id: str) -> None:
        """Start capturing network traffic for a specific job."""
        self.log_message("INFO", "scraper", f"Starting traffic capture for job: {job_id}")
        self.traffic_job_id = job_id
        self.traffic_data = []
        
        # Set up request listener
        async def handle_request(request):
            try:
                # Skip static assets
                if request.url.endswith(('.js', '.css', '.png', '.jpg', '.svg', '.woff', '.woff2', '.ttf', '.eot')):
                    return
                
                # Capture request
                self.traffic_data.append({
                    "ts": datetime.now().isoformat(),
                    "type": "request",
                    "url": request.url,
                    "method": request.method,
                    "headers": dict(request.headers),
                    "status": None,
                    "body": None
                })
            except Exception as e:
                self.log_message("WARN", "scraper", f"Request handler error: {e}")
        
        # Set up response listener
        async def handle_response(response):
            try:
                # Find matching request
                request_data = None
                for data in self.traffic_data:
                    if data["type"] == "request" and data["url"] == response.url:
                        request_data = data
                        break
                
                if request_data:
                    # Capture response
                    request_data["status"] = response.status()
                    request_data["body"] = await response.text()
                    
                    # Ensure JSON body is properly formatted
                    if request_data["body"]:
                        content_type = response.headers.get("content-type", "")
                        if "application/json" in content_type:
                            try:
                                import json
                                request_data["body"] = json.dumps(json.loads(request_data["body"]), indent=2)
                            except (json.JSONDecodeError, TypeError):
                                pass
            except Exception as e:
                self.log_message("WARN", "scraper", f"Response handler error: {e}")
        
        # Attach listeners
        try:
            await self.page.on("request", handle_request)
            await self.page.on("response", handle_response)
            self.log_message("INFO", "scraper", f"Traffic capture started for job: {job_id}")
        except Exception as e:
            self.log_message("ERROR", "scraper", f"Failed to attach traffic listeners: {e}")
    
    async def _stop_traffic_capture(self) -> None:
        """Stop traffic capture and save to file."""
        if not self.traffic_job_id:
            self.log_message("INFO", "scraper", "No active traffic capture to stop")
            return
        
        self.log_message("INFO", "scraper", f"Stopping traffic capture for job: {self.traffic_job_id}")
        
        try:
            # Remove listeners
            await self.page.off("request", lambda r: None)
            await self.page.off("response", lambda r: None)
            
            # Save to file
            output_path = f"/tmp/socleads_traffic_{self.traffic_job_id}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.traffic_data, f, indent=2, default=str)
            
            self.log_message("INFO", "scraper", f"Traffic saved to: {output_path}")
            self.log_message("INFO", "scraper", f"Total traffic entries: {len(self.traffic_data)}")
            
        except Exception as e:
            self.log_message("ERROR", "scraper", f"Failed to save traffic data: {e}")
        
        self.traffic_job_id = None
        self.traffic_data = []
    
    async def _check_job_status(self, job: ScrapeJob) -> ScrapeStatus:
        """Check the status of a job by polling."""
        try:
            # Look for status indicators on the page
            await self.page.wait_for_timeout(1000)
            
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
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
        
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
