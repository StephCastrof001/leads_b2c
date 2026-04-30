const firecrawl = require('firecrawl');
const API_KEY = process.env.FIRECRAWL_API_KEY;

const firecrawlClient = firecrawl(API_KEY);

async function enrichLeads(urls) {
  const results = [];
  
  for (const url of urls) {
    try {
      const response = await firecrawlClient.crawl({
        urls: [url],
        selectors: {
          phone: /(\+\?0?[\d\s-\.]{6,20})/g,
          email: /(?<![\w.])([\w\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})(?![\w.])(?![\.\w])/g
        },
        depth: 2,
        includePaths: ['/contacto', '/about', '/terms', '/contact', '/contact-us', '/info'],
        limit: 5
      });

      const crawledData = await response.data;
      console.log('Crawled:', url);
      console.log('Data:', JSON.stringify(crawledData, null, 2));
      results.push({ url, crawledData });
    } catch (error) {
      console.error('Error crawling', url, error);
    }
  }
  
  return results;
}

module.exports = { firecrawlClient, enrichLeads };