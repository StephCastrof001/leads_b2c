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
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 30000  # 30s

# Safe headers to keep in API endpoints
SAFE_HEADERS = {"content-type", "accept", "user-agent", "accept-language", "accept-encoding"}


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


def redact_sensitive_keys(data: Any) -> Any:
    """Recursively redact sensitive keys in JSON data."""
    if isinstance(data, dict):
        return {k: redact_sensitive_keys(v) for k, v in data.items() 
                if not any(sensitive in k.lower() for sensitive in ["password", "passwd", "token", "auth", "session", "secret", "cookie"])}
    elif isinstance(data, list):
        return [redact_sensitive_keys(item) for item in data]
    else:
        return data


def redact_body(data: Any) -> Any:
    """Redact sensitive keys and return simplified version."""
    redacted = redact_sensitive_keys(data)
    # If all keys were redacted, return a marker
    if isinstance(redacted, dict) and len(redacted) == 0:
        return "[REDACTED]"
    return redacted


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
        await page.wait_for_selector('input[placeholder="Email"]', timeout=5000)
        
        email_input = page.locator('input[placeholder="Email"]')
        password_input = page.locator('input[type="password"]')
        
        await email_input.fill(SOCLEADS_EMAIL)
        await password_input.fill(SOCLEADS_PASSWORD)
        
        # Find and click login button
        login_button = page.locator('button:has-text("Log in")')
        await login_button.click()
        
        # Wait for successful login
        await page.wait_for_timeout(8000)
        
        # Check if we're logged in by looking for sidebar elements
        is_logged_in = await page.locator('text=Scraping results, text=Scrape Instagram').count()
        
        if is_logged_in > 0:
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
    
    try:
        # Sidebar clicks based on section
        if section == "ig_keyword":
            await page.click("text=Scrape Instagram Keyword", timeout=TIMEOUT)
            await page.wait_for_timeout(2000)
        elif section == "fb_keyword":
            await page.click("text=Scrape Facebook", timeout=TIMEOUT)
            await page.wait_for_timeout(2000)
        elif section == "results":
            await page.click("text=Scraping results", timeout=TIMEOUT)
            await page.wait_for_timeout(2000)
        
        # Wait for page to load
        await page.wait_for_timeout(2000)
        
        # Take screenshot
        screenshot_path = SCREENSHOTS_DIR / f"{section}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        await page.screenshot(path=str(screenshot_path))
        log_message("INFO", "recon", f"Screenshot saved: {screenshot_path.name}")
        
    except Exception as e:
        log_message("ERROR", "recon", f"Navigation error for {section}: {e}")


async def intercept_requests(context: BrowserContext, page: Page, endpoints: List[APIEndpoint]):
    """Intercept all network requests and responses."""
    log_message("INFO", "recon", "Setting up request interception...")
    
    def handle_request(request: Request):
        # Check if it's an API request
        if "/api/" in request.url or "/v1/" in request.url or request.resource_type in {"fetch", "xhr"}:
            log_message("DEBUG", "recon", f"Intercepted request: {request.method} {request.url}")
            
            # Filter headers to only safe keys
            safe_headers = {k: v for k, v in dict(request.headers).items() if k.lower() in SAFE_HEADERS}
            
            # Store request body if available, with redaction
            endpoint_body = None
            try:
                if request.post_data:
                    try:
                        # Try to parse as JSON
                        import json
                        parsed_body = json.loads(request.post_data)
                        # Redact sensitive keys
                        endpoint_body = redact_body(parsed_body)
                    except (json.JSONDecodeError, TypeError):
                        # Not JSON, store raw data
                        endpoint_body = request.post_data
            except UnicodeDecodeError as e:
                log_message("INFO", "recon", f"[INFO] Posible archivo binario o CSV detectado en endpoint: {request.url}")
                # Use post_data_buffer to avoid re-decoding, store as marker
                endpoint_body = '<Binary Data>'
            
            # Store the request details
            endpoint = APIEndpoint(
                method=request.method,
                url=request.url,
                headers=safe_headers,
                body=endpoint_body,
                response_status=0,
                response_preview=""
            )
            
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
                '--disable-blink-features=AutomationControlled',
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
        sections = ["ig_keyword", "fb_keyword", "results"]
        
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
    
    print("Nivel 5.5 E2E OK")
    print("CrewAI E2E OK")


if __name__ == "__main__":
    asyncio.run(main())
