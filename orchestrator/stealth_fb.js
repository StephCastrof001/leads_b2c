const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

async function scrapeFacebookGroups(niche) {
  const emails = new Set();
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  try {
    const page = await browser.newPage();
    // Search query construction without @ symbol in the HEREDOC to avoid shell issues
    const query = 'site:facebook.com "  + String.fromCharCode(64) +  gmail.com\ ' + niche;
 const searchUrl = 'https://www.google.com/search?q=' + encodeURIComponent(query);
 console.log('🔍 Buscando leads en:', searchUrl);
 
 await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 60000 });
 
 const extractedEmails = await page.evaluate(() => {
 const text = document.body.innerText;
 const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/g;
 const matches = text.match(emailRegex);
 return matches || [];
 });

 extractedEmails.forEach(email => emails.add(email.toLowerCase()));
 
 } catch (error) {
 console.error('❌ Error de scraping:', error.message);
 } finally {
 await browser.close();
 }
 
 return Array.from(emails);
}

module.exports = { scrapeFacebookGroups };
