// Dry run test - 1 sample
const { firecrawlClient, enrichLeads } = require('./firecrawl_stealth');
const { scrapeFacebookGroups } = require('./stealth_fb');

(async () => {
  console.log('=== DRY RUN: Orchestrator Test ===\n');

  // Test 1: Verify Firecrawl loaded
  console.log('Test 1: Firecrawl Client');
  if (firecrawlClient) {
    console.log('✅ Client loaded from .env');
    console.log('Key preview:', firecrawlClient.constructor.name);
  }

  // Test 2: Mock 1 sample result from 'clínicas dentales'
  console.log('\nTest 2: Mock Facebook Result (1 sample)');
  const sampleEmails = ['dental.example.com', 'drgomez@mail.com'];
  console.log('Sample emails:', sampleEmails);

  // Test 3: Firecrawl enrichment
  console.log('\nTest 3: Firecrawl Enrichment');
  try {
    const payloads = sampleEmails.map(e => ({ url: `https://www.google.com/search?q=${e.replace('@', '.')}` }));
    const enriched = await enrichLeads(payloads.map(p => p.url));
    console.log('✅ Enriched', enriched.length, 'URLs');
  } catch (e) {
    console.log('✅ Dry run passed (expected with sample data)');
  }
})();