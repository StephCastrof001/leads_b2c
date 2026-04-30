const { default: FirecrawlApp } = require('firecrawl');
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '.env');
const envContent = fs.readFileSync(envPath, 'utf8');
const apiKey = envContent.match(/FIRECRAWL_API_KEY=(.*)/)?.[1]?.trim() || null;

const firecrawlClient = apiKey ? new FirecrawlApp({ apiKey }) : null;

async function enrichLeads(urls) {
  if (!firecrawlClient) {
    console.log('Warning: Firecrawl client not initialized');
    return [{ data: { contentLength: 0, content: 'No API Key', metadataUrls: {}, contactPerson: { name: 'N/A' } } }];
  }

  const results = [];
  const v1 = firecrawlClient.v1;
  
  for (const url of urls) {
    try {
      // Firecrawl v1 returns a Promise, wait for it
      const doc = await v1.scrapeUrl(url);
      
      // v1 returns document directly (not a promise)
      if (doc) {
        console.log('✅ Got result - status might vary by API version');
        results.push({ url, data: doc });
      } else {
        console.log('⚠️  Doc is object, checking structure');
        results.push({ url, data: doc || { contentLength: 500, content: 'Error', metadataUrls: {}, contactPerson: { name: 'N/A' } } });
      }
    } catch (error) {
      console.error('❌ Error:', url.slice(0, 50), error.message);
      results.push({ url, data: { contentLength: 500, content: 'Error', metadataUrls: {}, contactPerson: { name: 'N/A' } } });
    }
  }
  
  return results;
}

module.exports = { firecrawlClient, enrichLeads };
