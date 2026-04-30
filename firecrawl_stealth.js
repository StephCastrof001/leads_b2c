const { FirecrawlApp, default: FirecrawlAppV1 } = require('firecrawl');
const API_KEY = process.env.FIRECRAWL_API_KEY;

const firecrawlClient = new FirecrawlApp({ apiKey: API_KEY });

async function enrichLeads(urls) {
  const results = [];
  
  for (const url of urls) {
    try {
      const doc = await firecrawlClient.scrapeUrl(url, {
        selectors: {
          phone: /(\+\?0?[\d\s-\.]{6,20})/g,
          email: /(?<![\w.])([\w\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})(?![\w.])(?![\.\w])/g
        },
        formId: 0
      });

      console.log('Scraped:', url);
      console.log('Data:', JSON.stringify(doc, null, 2));
      results.push({ url, data: doc });
    } catch (error) {
      console.error('Error scraping', url, error);
    }
  }
  
  return results;
}

module.exports = { firecrawlClient, enrichLeads };