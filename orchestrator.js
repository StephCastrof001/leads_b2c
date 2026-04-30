const { scrapeFacebookGroups, extractAboutPage } = require('./stealth_fb');
const { firecrawlClient, enrichLeads } = require('./firecrawl_stealth');
const { URL } = require('url');

async function runPipeline(niche) {
  const fbEmails = await scrapeFacebookGroups(niche);
  
  // Build firecrawl URLs from business pages
  const urlsToCrawl = fbEmails.map(email => `https://www.facebook.com/search/people?query=${encodeURIComponent(email)}`);
  
  const enrichedData = await enrichLeads(urlsToCrawl);
  return { ...enrichedData, emails: fbEmails };
}

module.exports = { runPipeline };