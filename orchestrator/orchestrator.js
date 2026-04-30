const { createClient } = require('@supabase/supabase-js');
const { enrichLeads } = require('./firecrawl_stealth');
const { scrapeFacebookGroups } = require('./stealth_fb');
require('dotenv').config({ path: require('path').join(__dirname, '.env') });

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

async function saveLead(email, data) {
  const domain = email.split('@')[1]?.toLowerCase() || '';
  const isPersonal = ['gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com'].includes(domain);

  if (!isPersonal) {
    // B2B: Company
    const { error } = await supabase.from('companies').insert([
      { 
        company_name: email.split('@')[0].toUpperCase(), 
        website: domain,
        emails: [email],
        industry: 'Lead Extracted'
      }
    ]);
    if (!error) console.log('   -> [Supabase] ✅ Empresa guardada:', email);
    else console.error('   -> [Supabase] ❌ Error:', error.message);
  } else {
    // B2C: Individual
    const { error } = await supabase.from('individuals').insert([
      { 
        ig_handle: email.split('@')[0], 
        bio: 'Lead extracted from FB/IG search',
        is_private: false
      }
    ]);
    if (!error) console.log('   -> [Supabase] ✅ Persona guardada:', email);
    else console.error('   -> [Supabase] ❌ Error:', error.message);
  }
}

(async () => {
  console.log('=== 🚀 LANZAMIENTO REAL: EXTRACCIÓN DE LEADS ===\n');
  const niche = 'Clinicas Dentales en Lima';
  console.log('📢 Nicho:', niche);

  try {
    const emails = await scrapeFacebookGroups(niche);
    console.log('✅ Encontrados', emails.length, 'leads potenciales.\n');

    for (const email of emails.slice(0, 5)) {
      console.log('📑 Procesando:', email);
      // En un flujo real, aqui llamariamos a enrichLeads(email)
      // Pero para ver datos YA, vamos a guardarlos directo
      await saveLead(email, {});
    }

    console.log('\n✨ EXTRACCIÓN COMPLETADA. REVISA TU DASHBOARD.');
  } catch (err) {
    console.error('❌ Error en el orquestador:', err.message);
  }
})();
