import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

import async_playwright

# Load environment variables
load_dotenv()

SOCLEADS_EMAIL = os.getenv("SOCLEADS_EMAIL")
SOCLEADS_PASSWORD = os.getenv("SOCLEADS_PASSWORD")
SOCLEADS_BASE_URL = os.getenv("SOCLEADS_BASE_URL", "https://socleads.com")

# Storage for captured requests
captured_requests = []

# Stealth configuration
STEALTH_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--no-sandbox',
    '--disable-setuid-sandbox'
]

# Extensions to filter out
EXCLUDED_EXTENSIONS = ['.js', '.css', '.png', '.jpg', '.svg', '.woff', '.woff2', '.ttf', '.ico', '.eot']

# Allowed HTTP methods
ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']


def is_excluded_extension(url: str) -> bool:
    """Check if URL ends with an excluded extension."""
    url_lower = url.lower()
    for ext in EXCLUDED_EXTENSIONS:
        if url_lower.endswith(ext):
            return True
    return False


def is_allowed_method(method: str) -> bool:
    """Check if HTTP method is allowed."""
    return method.upper() in ALLOWED_METHODS


def create_request_data(route, request, response):
    """Create a data object from the intercepted request/response."""
    return {
        'ts': datetime.now().isoformat(),
        'url': request.url,
        'method': request.method,
        'request_headers': dict(request.headers),
        'request_body': request.post_data,
        'response_status': response.status,
        'response_body': response.text,
        'response_content_type': response.content_type
    }


async def route_handler(route, request):
    """Handler for intercepting requests."""
    # Check if URL is excluded
    if is_excluded_extension(request.url):
        await route.continue_()
        return

    # Check if method is allowed
    if not is_allowed_method(request.method):
        await route.continue_()
        return

    # Continue the request to get response
    response = await route.continue_()

    # Capture the request/response data
    data = create_request_data(route, request, response)
    captured_requests.append(data)


async def login(page):
    """Login to SocLeads using email and password."""
    # Find and fill login form
    email_input = page.locator('input[type="email"]')
    password_input = page.locator('input[type="password"]')
    login_button = page.locator('button[type="submit"]')

    await email_input.fill(SOCLEADS_EMAIL)
    await password_input.fill(SOCLEADS_PASSWORD)
    await login_button.click()

    # Wait for login to complete
    await asyncio.sleep(3)


async def run_scrape_job(page):
    """Navigate to Scrape Instagram Keyword and run a test job."""
    # Navigate to the keyword scrape page
    await page.goto(SOCLEADS_BASE_URL + "/scrape/instagram/keyword")
    
    # Wait for page to load
    await asyncio.sleep(1)

    # Fill in the keyword
    keyword_input = page.locator('input[name="keyword"]')
    await keyword_input.fill("Marketing")

    # Fill in the results count
    results_input = page.locator('input[name="results"]')
    await results_input.fill("10")

    # Click Search
    search_button = page.locator('button[type="submit"]')
    await search_button.click()

    # Wait for job to complete (15 seconds)
    await asyncio.sleep(15)


async def main():
    """Main function to run the API recon capture."""
    print("[INFO] Starting SocLeads API Recon Capture...")
    print(f"[INFO] Base URL: {SOCLEADS_BASE_URL}")
    print(f"[INFO] Email: {SOCLEADS_EMAIL}")
    print("[INFO] Password: [REDACTED]")

    async with async_playwright.async_playwright() as p:
        # Launch browser with stealth settings
        browser = await p.chromium.launch(
            args=STEALTH_ARGS,
            headless=True,
            ignore_https_errors=True
        )

        # Create a new context and page
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        print("[INFO] Browser launched successfully")

        # Navigate to base URL
        await page.goto(SOCLEADS_BASE_URL)
        print("[INFO] Navigated to base URL")

        # Set up route interception
        await page.route("**/*", route_handler)
        print("[INFO] Route interception enabled")

        # Login
        await login(page)
        print("[INFO] Login completed")

        # Wait a bit after login
        await asyncio.sleep(2)

        # Run the scrape job
        await run_scrape_job(page)
        print("[INFO] Scrape job completed")

        # Unroute all handlers
        await page.unroute_all()
        print("[INFO] Route interception disabled")

        # Save captured requests to file
        output_path = "/tmp/socleads_api_recon.json"
        with open(output_path, 'w') as f:
            json.dump(captured_requests, f, indent=2)
        print(f"[INFO] Captured requests saved to: {output_path}")

        # Print summary
        total_requests = len(captured_requests)
        unique_urls = set(req['url'] for req in captured_requests)

        print("\n" + "=" * 60)
        print("RECON API CAPTURE SUMMARY")
        print("=" * 60)
        print(f"Total requests captured: {total_requests}")
        print(f"Unique URLs: {len(unique_urls)}")
        print("\nUnique URLs captured:")
        for url in sorted(unique_urls):
            print(f"  - {url}")
        print("=" * 60)

        # Close browser
        await browser.close()
        print("[INFO] Browser closed")


if __name__ == "__main__":
    asyncio.run(main())
