import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import axios from 'axios';
import { writeFileSync, existsSync, readFileSync } from 'fs';
import * as dotenv from 'dotenv';
dotenv.config();

const firebaseConfig = {
  apiKey: 'AIzaSyCLF2A2phVTJVChOcWq-lk6bOoY9hXUAGs',
  authDomain: 'mailerfind-dev.firebaseapp.com',
  projectId: 'mailerfind',
  storageBucket: 'mailerfind.appspot.com',
  messagingSenderId: '297926607424',
  appId: '1:297926607424:web:98da15637df76fc03715a5',
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const API = 'https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI';
const FIRECRAWL_API_KEY = process.env.FIRECRAWL_API_KEY;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Distritos de Lima
const distritos = [
  'lima', 'miraflores', 'san isidro', 'surco', 'san borja', 'lince', 'jesus maria',
  'magdalena', 'pueblo libre', 'san miguel', 'los olivos', 'independencia', 
  'comas', 'san martin de porres', 'ate', 'santa anita', 'san juan de lurigancho',
  'san juan de miraflores', 'villa el salvador', 'chorrillos'
];

// Nichos B2B
const nichos = [
  'clinica dental',
  'dentista',
  'insumos dentales',
  'equipos dentales',
  'materiales dentales',
  'ferreteria',
  'herramientas',
  'materiales de construccion',
  'distribuidor ferretero'
];

async function main() {
  console.log('--- B2B Instagram Crawler (Mailerfind Search + Firecrawl) ---');
  
  if (!FIRECRAWL_API_KEY) {
    console.log('⚠️ ADVERTENCIA: No se encontro FIRECRAWL_API_KEY en .env. El enriquecimiento web fallara.');
  }

  // 1. LOGIN MAILERFIND
  const cred = await signInWithEmailAndPassword(auth, 'steph@colega.lat', '20063288smcF');
  const token = await cred.user.getIdToken();
  const headers = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };
  console.log('✅ Auth Firebase Mailerfind OK');

  // 2. GENERAR QUERIES
  const queries = [];
  for (const n of nichos) {
    for (const d of distritos) {
      queries.push(`${n} ${d}`);
    }
  }
  console.log(`🔍 Generadas ${queries.length} busquedas combinadas (Nicho x Distrito)`);
  
  // Usar solo un sample de 30 para no demorar horas en esta prueba
  const sampleQueries = queries.sort(() => 0.5 - Math.random()).slice(0, 30);
  console.log(`⏱️  Corriendo ${sampleQueries.length} busquedas para esta sesion...`);

  const seenPks = new Set();
  const leads = [];

  // 3. SEARCH LOOP (Rate limited)
  for (const q of sampleQueries) {
    try {
      console.log(`\nBuscando: [${q}]...`);
      const res = await axios.post(API + '/v1/instagram/search-users', { query: q }, { headers });
      await sleep(1000); // 1s pause
      
      const users = res.data.users || [];
      console.log(`  Encontrados: ${users.length} resultados`);

      for (const item of users) {
        const u = item.user || item;
        if (!seenPks.has(u.pk)) {
          seenPks.add(u.pk);
          
          // 4. GET PROFILE (Rate limited)
          try {
            const pRes = await axios.get(API + '/v1/instagram/user/' + u.username, { headers });
            await sleep(800); // 0.8s pause
            
            const profile = pRes.data.user;
            
            const lead = {
              username: profile.username,
              name: profile.full_name || profile.username,
              followers: profile.follower_count,
              category: profile.category || '',
              bio: profile.biography ? profile.biography.replace(/\\n/g, ' ').replace(/;/g, ',') : '',
              ig_website: profile.external_url || '',
              ig_email: profile.public_email || '',
              ig_phone: profile.public_phone_number || profile.contact_phone_number || '',
              city: profile.city_name || '',
              query_source: q,
              enriched_website: '',
              scraped_email: '',
              scraped_phone: '',
              scraped_address: ''
            };

            // 5. FIRECRAWL ENRICHMENT
            if (lead.ig_website && FIRECRAWL_API_KEY && !lead.ig_website.includes('instagram.com')) {
              try {
                // Scrape the main page using markdown format
                const fcRes = await axios.post('https://api.firecrawl.dev/v1/scrape', {
                  url: lead.ig_website,
                  formats: ['markdown'],
                  timeout: 15000 // 15s wait max
                }, {
                  headers: { 'Authorization': `Bearer ${FIRECRAWL_API_KEY}`, 'Content-Type': 'application/json' }
                });
                
                if (fcRes.data && fcRes.data.success && fcRes.data.data) {
                  const md = fcRes.data.data.markdown || '';
                  lead.enriched_website = fcRes.data.data.metadata?.sourceURL || lead.ig_website;
                  
                  // Regex basicos
                  const emailMatch = md.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
                  const phoneMatch = md.match(/(?:\+?51)?\s*9\d{2}\s*\d{3}\s*\d{3}|(?:\+?51)?\s*0[1-9]\s*\d{3}\s*\d{4}/);
                  // Buscar linea que contenga Av., Calle, Jr.
                  const addressMatch = md.match(/(?:Av\.|Avenida|Calle|Jr\.|Jirón) [a-zA-Z0-9\s]+ \d{2,4}/i);

                  if (emailMatch) lead.scraped_email = emailMatch[0];
                  if (phoneMatch) lead.scraped_phone = phoneMatch[0];
                  if (addressMatch) lead.scraped_address = addressMatch[0];
                }
              } catch(fcErr) {
                // Just log silently to console
                // console.log(`    Firecrawl err en ${lead.ig_website}`);
              }
            }

            console.log(`    + @${lead.username} | Email: ${lead.ig_email || lead.scraped_email || 'NO'} | Tel: ${lead.ig_phone || lead.scraped_phone || 'NO'} | Web: ${lead.ig_website ? 'SI' : 'NO'}`);
            leads.push(lead);

          } catch(e) {
            // console.log(`  Error obteniendo perfil de @${u.username}`);
            await sleep(1000);
          }
        }
      }
    } catch(e) {
      console.log(`  Error buscando [${q}]: ${e.message}`);
      await sleep(2000); // 2s pause on error
    }
  }

  // 6. EXPORTAR A CSV y JSON
  writeFileSync('leads_b2b_lima.json', JSON.stringify(leads, null, 2));
  
  if (leads.length > 0) {
    const csvHeaders = Object.keys(leads[0]).join(';');
    const csvRows = leads.map(l => Object.values(l).map(v => `"${String(v).replace(/"/g, '""')}"`).join(';'));
    writeFileSync('leads_b2b_lima.csv', [csvHeaders, ...csvRows].join('\n'));
  }

  console.log(`\n🎉 COMPLETADO! ${leads.length} leads B2B extraidos guardados en leads_b2b_lima.csv y .json`);
  process.exit(0);
}

main().catch(console.error);
