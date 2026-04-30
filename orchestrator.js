const { scrapeFacebookGroups, extractAboutPage } = require('./stealth_fb');
const { firecrawlClient, enrichLeads } = require('./firecrawl_stealth');

async function runPipeline(niche) {
  const fbEmails = await scrapeFacebookGroups(niche);
  
  const urlsToCrawl = fbEmails.map(email => `https://www.facebook.com/search/people?query=${encodeURIComponent(email)}`);
  
  const enrichedData = await enrichLeads(urlsToCrawl);
  return { ...enrichedData, emails: fbEmails };
}

module.exports = { runPipeline };