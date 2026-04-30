import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import axios from 'axios';

const firebaseConfig = {
  apiKey: 'REDACTED_API_KEY',
  authDomain: 'mailerfind-dev.firebaseapp.com',
  projectId: 'mailerfind',
  storageBucket: 'mailerfind.appspot.com',
  messagingSenderId: '297926607424',
  appId: '1:297926607424:web:98da15637df76fc03715a5',
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const API = 'https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI';

const cred = await signInWithEmailAndPassword(auth, 'steph@colega.lat', '20063288smcF');
const token = await cred.user.getIdToken();
const headers = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };

console.log('AUTH OK');

// 1) DUMP completo de /v1/prospects (con paginacion si existe)
console.log('\n=== /v1/prospects COMPLETO ===');
try {
  const res = await axios.get(API + '/v1/prospects', { headers });
  const prospects = res.data.data ? res.data.data.prospects : (res.data.prospects || []);
  console.log('Total en API:', prospects.length);
  
  let emailCount = 0;
  let phoneCount = 0;
  let websiteCount = 0;
  let bizCount = 0;
  
  for (const p of prospects) {
    if (p.email) emailCount++;
    if (p.phone_number) phoneCount++;
    if (p.website) websiteCount++;
    if (p.is_business) bizCount++;
    
    // Solo mostrar los que tienen datos utiles
    if (p.email || p.phone_number || p.website || p.is_business) {
      console.log('  @' + p.username + ' | email: ' + (p.email || '-') + ' | phone: ' + (p.phone_number || '-') + ' | web: ' + (p.website || '-') + ' | biz: ' + p.is_business + ' | followers: ' + p.followers);
    }
  }
  
  console.log('\nRESUMEN:');
  console.log('  Total prospects:', prospects.length);
  console.log('  Con email:', emailCount);
  console.log('  Con phone:', phoneCount);
  console.log('  Con website:', websiteCount);
  console.log('  Business:', bizCount);
} catch(e) {
  console.log('Error:', e.response ? JSON.stringify(e.response.data).substring(0, 500) : e.message);
}

// 2) Intentar buscar con query params (paginacion, filtros)
console.log('\n=== INTENTAR PAGINACION/FILTROS ===');
const queries = [
  '/v1/prospects?limit=100',
  '/v1/prospects?page=1&limit=100',
  '/v1/prospects?offset=0&limit=100',
  '/v1/prospects?analysisId=SpMkSYd5y0VwkIOO6ivL',
];

for (const q of queries) {
  try {
    const res = await axios.get(API + q, { headers });
    const data = res.data.data ? res.data.data : res.data;
    const count = data.prospects ? data.prospects.length : (data.length || 'N/A');
    const total = data.total || data.totalCount || 'N/A';
    console.log('[200] ' + q + ' => count: ' + count + ', total: ' + total);
  } catch(e) {
    const status = e.response ? e.response.status : 'ERR';
    console.log('[' + status + '] ' + q);
  }
}

// 3) Endpoint de analisis - variantes
console.log('\n=== VARIANTES DE ANALYSIS ENDPOINT ===');
const analysisEndpoints = [
  '/v1/analysis/SpMkSYd5y0VwkIOO6ivL',
  '/v1/analysis?id=SpMkSYd5y0VwkIOO6ivL',
  '/v1/analysis/get/SpMkSYd5y0VwkIOO6ivL',
  '/v1/analysis/status/SpMkSYd5y0VwkIOO6ivL',
];

for (const ep of analysisEndpoints) {
  try {
    const res = await axios.get(API + ep, { headers });
    console.log('[200] GET ' + ep + ' => ' + JSON.stringify(res.data).substring(0, 400));
  } catch(e) {
    const status = e.response ? e.response.status : 'ERR';
    const msg = e.response ? JSON.stringify(e.response.data).substring(0, 150) : e.message;
    console.log('[' + status + '] GET ' + ep + ' => ' + msg);
  }
}

// 4) Instagram user search - como lo hace el frontend
console.log('\n=== INSTAGRAM SEARCH VARIANTES ===');
const searchEndpoints = [
  '/v1/instagram/user/clinica_internacional',
  '/v1/instagram/user/dentista_lima_peru',
  '/v1/instagram/user/clinicadentalsonrisa',
  '/v1/instagram/search?q=clinica+dental+lima',
  '/v1/instagram/search/clinica',
  '/v1/account-finder?q=clinica+dental',
  '/v1/account-finder?username=clinica_internacional',
];

for (const ep of searchEndpoints) {
  try {
    const res = await axios.get(API + ep, { headers });
    const d = res.data;
    if (d.user) {
      console.log('[200] ' + ep + ' => @' + d.user.username + ' | followers: ' + d.user.follower_count + ' | web: ' + (d.user.external_url || '-') + ' | email_pub: ' + (d.user.public_email || '-') + ' | phone_pub: ' + (d.user.public_phone_number || '-') + ' | biz: ' + (d.user.is_business || '-'));
    } else {
      console.log('[200] ' + ep + ' => ' + JSON.stringify(d).substring(0, 300));
    }
  } catch(e) {
    const status = e.response ? e.response.status : 'ERR';
    console.log('[' + status + '] ' + ep);
  }
}

process.exit(0);
