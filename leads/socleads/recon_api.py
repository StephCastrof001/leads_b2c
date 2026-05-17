import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from playwright.async_api import async_playwright, BrowserContext, Page, Request, Response
from playwright.async_api import Route

# Configuration
SOCLEADS_EMAIL = os.getenv('SOCLEADS_EMAIL', 'test@example.com')
SOCLEADS_PASSWORD = os.getenv('SOCLEADS_PASSWORD', 'test123')
SOCLEADS_URL = os.getenv('SOCLEADS_URL', 'https://socleads.com')

# Storage
TRAFFIC_DIR = os.path.join(os.path.dirname(__file__), 'traffic')
TRAFFIC_FILE = os.path.join(TRAFFIC_DIR, 'captured_requests.json')

# Global storage
captured_requests: List[Dict[str, Any]] = []


def is_excluded_extension(url: str) -> bool:
    """Check if URL has excluded extensions (e.g., images, scripts, etc.)"""
    excluded = ['.png', '.jpg', '.gif', '.css', '.js', '.woff', '.woff2', '.svg', '.ico', '.pdf']
    return any(url.lower().endswith(ext) for ext in excluded)


def is_allowed_method(method: str) -> bool:
    """Check if HTTP method is allowed for capture"""
    allowed = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
    return method.upper() in allowed


def create_request_data(route: Route, request: Request, response: Response) -> Dict[str, Any]:
    """Create a data structure for a captured request"""
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


async def setup_directories() -> None:
    """Ensure traffic directory exists"""
    os.makedirs(TRAFFIC_DIR, exist_ok=True)


async def login(context: BrowserContext, page: Page) -> bool:
    """Login to Sockleads"""
    try:
        await page.goto(SOCLEADS_URL)
        # Fill in credentials
        await page.fill('input[name="email"]', SOCKLEADS_EMAIL)
        await page.fill('input[name="password"]', SOCKLEADS_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_selector('.dashboard', timeout=5000)
        return True
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return False


async def navigate_and_capture(context: BrowserContext, page: Page, section: str) -> None:
    """Navigate to a specific section and capture traffic"""
    try:
        await page.goto(SOCLEADS_URL + f"/{section}")
        await page.wait_for_load_state('networkidle', timeout=10000)
        print(f"[INFO] Captured traffic for section: {section}")
    except Exception as e:
        print(f"[ERROR] Navigation failed: {e}")


async def intercept_requests(context: BrowserContext, page: Page, endpoints: List[Dict[str, Any]]) -> None:
    """Intercept all network requests and responses."""
    async def route_handler(route: Route, request: Request):
        if is_excluded_extension(request.url) or not is_allowed_method(request.method):
            await route.continue_()
            return
        try:
            response = await route.fetch()
            await route.fulfill(response=response)
            data = {
                'ts': datetime.now().isoformat(),
                'url': request.url,
                'method': request.method,
                'request_headers': dict(request.headers),
                'request_body': request.post_data,
                'response_status': response.status,
                'response_body': await response.text(),
                'response_content_type': response.headers.get('content-type', '')
            }
            captured_requests.append(data)
        except Exception:
            await route.continue_()

    await context.route('**/*', route_handler)


async def main() -> None:
    """Main entry point"""
    print(f"[INFO] Starting Sockleads Recon API...")
    print(f"[INFO] Email: {SOCLEADS_EMAIL}")
    
    # Setup directories
    await setup_directories()
    
    # Create Playwright context
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Setup traffic capture
        await intercept_requests(context, page, [])
        
        # Login
        if await login(context, page):
            print(f"[INFO] Login successful")
            
            # Navigate and capture
            await navigate_and_capture(context, page, 'dashboard')
            await navigate_and_capture(context, page, 'leads')
            
            # Save results
            await save_results()
            
            # Summary
            print(f"[INFO] Captured {len(captured_requests)} requests")
        else:
            print(f"[ERROR] Login failed")
        
        await browser.close()


async def save_results() -> None:
    """Save captured requests to file"""
    try:
        with open(TRAFFIC_FILE, 'w') as f:
            json.dump(captured_requests, f, indent=2)
        print(f"[INFO] Results saved to {TRAFFIC_FILE}")
    except Exception as e:
        print(f"[ERROR] Save failed: {e}")


if __name__ == '__main__':
    asyncio.run(main())
