import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from playwright.async_api import async_playwright, BrowserContext, Page, Request, Response

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SOCLEADS_BASE_URL = os.getenv("SOCLEADS_BASE_URL", "https://app.socleads.com")
SOCLEADS_EMAIL = os.getenv("SOCLEADS_EMAIL")
SOCLEADS_PASSWORD = os.getenv("SOCLEADS_PASSWORD")
API_MAP_DIR = Path(os.getenv("API_MAP_DIR", "recon/api_map"))
SCREENSHOTS_DIR = Path(os.getenv("SCREENSHOTS_DIR", "recon/screenshots"))
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120"
TIMEOUT = 30000  # 30s


class APIEndpoint:
    def __init__(self, method: str, url: str, headers: Dict, body: Any, 
                 response_status: int, response_preview: str):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.response_status = response_status
        self.response_preview = response_preview


def log_message(level: str, module: str, message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] [{module}] {message}")


async def setup_directories():
    """Create required directories if they don't exist."""
    API_MAP_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


async def login(context: BrowserContext, page: Page) -> bool:
    """Login to SocLeads."""
    log_message("INFO", "recon", "Starting login...")
    
    await page.goto(SOCLEADS_BASE_URL, timeout=TIMEOUT)
    
    # Wait for login form and fill credentials
    try:
        # Try to find login form elements
        await page.wait_for_selector('input[type="email"]', timeout=5000)
        
        email_input = page.locator('input[type="email"]')
        password_input = page.locator('input[type="password"]')
        
        await email_input.fill(SOCLEADS_EMAIL)
        await password_input.fill(SOCLEADS_PASSWORD)
        
        # Find and click login button
        login_button = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Ingresar")')
        await login_button.click()
        
        # Wait for successful login (check for dashboard or user menu)
        await page.wait_for_timeout(2000)
        
        # Check if we're logged in by looking for dashboard elements
        is_logged_in = await page.wait_for_selector(
            'div:has-text("Dashboard"), div:has-text("Scraper"), div:has-text("History")',
            timeout=5000
        )
        
        if is_logged_in:
            log_message("INFO", "recon", "Login successful!")
            return True
        else:
            log_message("WARN", "recon", "Login might not be successful, checking page URL...")
            return False
            
    except Exception as e:
        log_message("ERROR", "recon", f"Login error: {e}")
        return False


async def navigate_and_capture(context: BrowserContext, page: Page, section: str):
    """Navigate to a section and capture requests/screenshots."""
    log_message("INFO", "recon", f"Navigating to {section}...")
    
    # Build URL for the section
    url = f"{SOCLEADS_BASE_URL}/{section}"
    
    try:
        await page.goto(url, timeout=TIMEOUT)
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle", timeout=TIMEOUT)
        
        # Take screenshot
        screenshot_path = SCREENSHOTS_DIR / f"{section}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=str(screenshot_path))
        log_message("INFO", "recon", f"Screenshot saved: {screenshot_path.name}")
        
        # Wait a bit for any lazy-loaded content
        await page.wait_for_timeout(2000)
        
    except Exception as e:
        log_message("ERROR", "recon", f"Navigation error for {section}: {e}")


async def intercept_requests(context: BrowserContext, page: Page, endpoints: List[APIEndpoint]):
    """Intercept all network requests and responses."""
    log_message("INFO", "recon", "Setting up request interception...")
    
    def handle_request(request: Request):
        # Check if it's an API request
        if '/api/' in request.url or '/v1/' in request.url or request.url.endswith('.fetch') or request.url.endswith('.xhr'):
            log_message("DEBUG", "recon", f"Intercepted request: {request.method} {request.url}")
            
            # Store the request details
            endpoint = APIEndpoint(
                method=request.method,
                url=request.url,
                headers=dict(request.headers),
                body=None,
                response_status=0,
                response_preview=""
            )
            
            # Store request body if available
            if request.post_data:
                endpoint.body = request.post_data
            
            # Store request
            endpoints.append(endpoint)

    
    def handle_response(response: Response):
        # Update response info for stored endpoints
        for endpoint in endpoints:
            if endpoint.url == response.url:
                endpoint.response_status = response.status
                try:
                    endpoint.response_preview = "(captured)"
                except:
                    endpoint.response_preview = "Binary response"
                break
    
    # Set up request interception
    page.on("request", handle_request)
    page.on("response", handle_response)
    
    log_message("INFO", "recon", "Request interception active")


async def main():
    """Main function to run the API mapper."""
    log_message("INFO", "recon", "=== Starting SocLeads API Mapper ===")
    
    # Setup directories
    await setup_directories()
    
    # Create browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                f'--user-agent={USER_AGENT}'
            ]
        )
        
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        # Setup request interception
        endpoints: List[APIEndpoint] = []
        await intercept_requests(context, page, endpoints)
        
        # Login
        logged_in = await login(context, page)
        if not logged_in:
            log_message("WARN", "recon", "Login failed, continuing with available data...")
        
        # Navigate through sections
        sections = ["dashboard", "scraper", "history", "account", "billing"]
        
        for section in sections:
            await navigate_and_capture(context, page, section)
        
        # Close browser
        await browser.close()
    
    # Save API endpoints
    log_message("INFO", "recon", f"Found {len(endpoints)} API endpoints")
    
    # Save to file
    endpoints_file = API_MAP_DIR / "endpoints.json"
    with open(endpoints_file, 'w', encoding='utf-8') as f:
        json.dump([
            {
                "method": e.method,
                "url": e.url,
                "headers": e.headers,
                "body": e.body,
                "response_status": e.response_status,
                "response_preview": e.response_preview
            }
            for e in endpoints
        ], f, indent=2, default=str)
    
    log_message("INFO", "recon", f"Endpoints saved to: {endpoints_file}")
    
    # Print table of endpoints
    print("\n" + "="*80)
    print("API ENDPOINTS FOUND")
    print("="*80)
    print(f"{'Method':<10} {'URL':<60} {'Status':<10}")
    print("-"*80)
    
    for endpoint in endpoints:
        # Truncate URL for display
        url_display = endpoint.url[:58] + ".." if len(endpoint.url) > 60 else endpoint.url
        status = f"{endpoint.response_status}" if endpoint.response_status else "Pending"
        print(f"{endpoint.method:<10} {url_display:<60} {status:<10}")
    
    print("="*80)
    print(f"Total endpoints: {len(endpoints)}")
    print(f"Saved to: {endpoints_file}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
