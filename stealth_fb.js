const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

async function scrapeFacebookGroups(niche) {
  const keywords = niche.split(',');
  const emails = new Set();
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  try {
    const groups = await searchFacebookGroups(keywords, browser);
    
    for (const group of groups.slice(0, 5)) {
      for (const pageUrl of [group.aboutUrl, group.webUrl]) {
        const data = await extractAboutPage(pageUrl, browser.clone());
        emails.add(data.email);
      }
    }
  } catch (error) {
    console.error('Scraping error:', error);
  } finally {
    await browser.close();
  }
  
  return Array.from(emails);
}

async function extractAboutPage(url, browser) {
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
  
  const content = await page.content();
  const email = await page.evaluate(() => {
    const selectors = ['a.email-link', 'a[href*="@gmail.com"]', 'a[href*="@outlook.com"]', 
                       'a[href*="@hotmail.com"]', 'a[href*="@yahoo.com"]', 'a[href*="@icloud.com"]',
                       '[class*="social-contact"]', '[title*="email"]', '[role="link"] a[href*="mailto"]'];
    
    for (const sel of selectors) {
      const link = document.querySelector(sel);
      if (link) {
        const href = link.getAttribute('href');
        if (href && /^mailto:/.test(href)) {
          return href.replace('mailto:', '');
        }
        const match = href.match(/[\w\.-]+@[\da-z\.-]+\.([a-z\.]{2,6})/i);
        if (match) return match[0];
      }
    }
    
    return null;
  });
  
  await page.close();
  return { email, content };
}

async function searchFacebookGroups(keywords, browser) {
  const page = await browser.newPage();
  await page.goto('https://www.facebook.com/groups', { waitUntil: 'networkidle0' });
  
  // Search query injection
  const searchQuery = keywords.slice(0, 2).join('+').replace(/[^a-zA-Z0-9\s]/g, '');
  const searchUrl = `https://www.google.com/search?q=site:facebook.com/groups+${keywords.join('+')}`;
  
  const page2 = await browser.newPage();
  await page2.goto(searchUrl, { waitUntil: 'networkidle0' });
  
  const groupUrls = await page2.evaluate(() => {
    return document.querySelectorAll('a[href*="facebook.com/groups"]')
      .map(a => a.href);
  });
  
  await page2.close();
  return groupUrls;
}

module.exports = { scrapeFacebookGroups, extractAboutPage };