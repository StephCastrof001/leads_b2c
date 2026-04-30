const { scrapeFB, scrapeIG } = require('./stealth_fb');
const firecrawl = require('./firecrawl_stealth');

async function runPipeline(niche) {
  const rawData = await scrapeFB(niche);
  const enrichedData = await firecrawl.process(rawData);
  return enrichedData;
}

module.exports = { runPipeline };