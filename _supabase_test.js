const { createClient } = require('@supabase/supabase-js');
const { enrichLeads } = require('./firecrawl_stealth');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

console.log('=== DRY RUN SUPABASE + FIRECRAWL ===\n');
console.log('SUPABASE_URL?', SUPABASE_URL ? '✅' : '❌ (use .env.example)');
console.log('SUPABASE_KEY?', SUPABASE_KEY ? '✅' : '❌');

(async () => {
  const db = createClient(SUPABASE_URL, SUPABASE_KEY);
  
  // Test 1: Tables exist
  console.log('\n🧪 Test 1: Verify tables');
  try {
    await db.rpc('upsert_company', { name: 'Clinica Test', email: 'test@test.com' });
    await db.rpc('upsert_individual', { full_name: 'Juan Perez', email: 'juan@test.com', phone: '+51911111111' });
    console.log('✅ Tables UPserted successfully');
  } catch (e) {
    console.log('Table errors:', e.message);
  }

  // Test 2: Firecrawl with 1 sample
  console.log('\n🧪 Test 2: Firecrawl + 1 sample');
  try {
    const sampleUrl = 'https://www.google.com/search?q=test+clinic';
    console.log('URL:', sampleUrl);
    const enriched = await enrichLeads([sampleUrl]);
    console.log('✅ Enriched', enriched.length, 'results');
    console.log('Sample length:', enriched[0]?.data?.contentLength || 0, 'chars');
  } catch (e) {
    console.log('Firecrawl:', e.message);
  }
})();
