const { createClient } = require('@supabase/supabase-js');
const { firecrawlClient, enrichLeads } = require('./firecrawl_stealth');
const { scrapeFacebookGroups } = require('./stealth_fb');
const fs = require('fs');

// === SUPABASE CONFIG ===
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// === SUPABASE UPDATER ===
async function upsertToSupabase(email, data) {
  const result = await Promise.all([
    // Companies table
    supabase.rpc('upsert_company', {
      name: data.companyName || 'N/A',
      email,
      website: data.metadataUrls?.site?.[0]?.['#text'] || ''
    }),
    // Individuals table  
    supabase.rpc('upsert_individual', {
      full_name: data.contactPerson || 'N/A',
      email,
      phone: data.phone?.[0]?.['#text'] || '',
      website: data.metadataUrls?.site?.[0]?.['#text'] || ''
    })
  ]);
  return { companies: !result[0].error, individuals: !result[1].error };
}

// === CLASSIFY LEADS ===
function classifyLead(email) {
  const domain = email.split('@')[1]?.toLowerCase() || '';
  const keywords = {
    b2b: ['corp', 'solutions', 'group', 'company', 'labs', 'clinic', 'centro', 'hospital', 'dental', 'odontologia', 'grupos', 'negocios', 'corporations'],
    b2c: ['gmail', 'hotmail', 'outlook', 'yahoo', 'person', 'personal', 'clincidental', 'clinicavesalio', 'clinicadental']
  };

  const b2b = keywords.b2b.some(k => domain.includes(k));
  const b2c = keywords.b2c.some(k => domain.includes(k));
  return { b2b, b2c };
}

// === MAIN EXECUTION ===
(async () => {
  console.log('=== ORCHESTRATOR: Orchestrator Flow ===\n');
  
  const niche = 'Clinica en lima peru';
  console.log(`📢 Niche: ${niche}`);

  const emails = await scrapeFacebookGroups(niche);
  console.log(`✅ Found ${emails.length} emails from FB/IG:`);
  
  for (const e of emails.slice(0, 5)) {
    const url = `https://www.google.com/search?q=${encodeURIComponent(e)}`;
    
    console.log(`\n📑 Processing: ${e}`);
    const enriched = await enrichLeads([url]);
    const item = enriched[0]?.data || enriched[0];
    
    if (item) {
      console.log(`   Type: ${item.companyName ? 'B2B' : item.contactPerson ? 'B2C' : 'HYBRID'}`);
      
      if (item.contactPerson?.name) {
        console.log(`   Person: ${item.contactPerson.name}`);
        console.log(`   Phone: ${item.phone?.[0]?.['#text']}`);
      }
      
      if (item.companyName) {
        console.log(`   Company: ${item.companyName.split(' ')[0]}`);
        console.log(`   Website: ${item.metadataUrls?.site?.[0]?.['#text'] || 'N/A'}`);
      }
    }
  })();
})().catch(console.error);
