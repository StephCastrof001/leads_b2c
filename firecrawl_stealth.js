const { default: FirecrawlApp } = require('firecrawl');
const fs = require('fs');
const path = require('path');

// Load .env
const envPath = path.join(__dirname, '.env');
const envContent = fs.readFileSync(envPath, 'utf8');
const apiKey = envContent.match(/FIRECRAWL_API_KEY=(.*)/)?.[1]?.trim() || null;

const firecrawlClient = apiKey ? new FirecrawlApp({ apiKey }) : null;

async function enrichLeads(urls) {
  if (!firecrawlClient) {
    console.log('Error: Firecrawl client not initialized');
    return [];
  }

  const results = [];
  const v1 = firecrawlClient.v1;
  
  for (const url of urls) {
    try {
      const doc = await v1.scrapeUrl(url);
      console.log('✅ Scrape:', url.slice(0, 100));
      results.push({ url, data: doc });
    } catch (error) {
      console.error('❌ Error:', url.slice(0, 50), error.message);
    }
  }
  
  return results;
}

module.exports = { firecrawlClient, enrichLeads };