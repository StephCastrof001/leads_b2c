import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import { getFirestore, doc, getDoc, collection, getDocs } from 'firebase/firestore';
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
const db = getFirestore(app);
const API = 'https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI';

const cred = await signInWithEmailAndPassword(auth, 'steph@colega.lat', '20063288smcF');
const token = await cred.user.getIdToken();
const uid = cred.user.uid;
const headers = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };

console.log('AUTH OK. UID:', uid);

// ======= PASO 0: VERIFICAR CREDITOS ANTES =======
console.log('\n=== PASO 0: CREDITOS ANTES ===');
try {
  const userDoc = await getDoc(doc(db, 'users', uid));
  const data = userDoc.data();
  console.log('Plan:', data.plan);
  console.log('AI Credits:', JSON.stringify(data.aiCredits));
  console.log('Credits (si existe):', data.credits || 'no definido');
  console.log('Subscription:', data.stripeSubscriptionId);
  // Buscar cualquier campo que diga "credit"
  for (const [k, v] of Object.entries(data)) {
    if (k.toLowerCase().includes('credit') || k.toLowerCase().includes('quota') || k.toLowerCase().includes('limit') || k.toLowerCase().includes('usage')) {
      console.log('  ' + k + ':', JSON.stringify(v));
    }
  }
} catch(e) { console.log('Error leyendo user doc:', e.message); }

// ======= PASO 1: BUSCAR clinica_internacional (GRATIS) =======
console.log('\n=== PASO 1: BUSCAR clinica_internacional ===');
let userInfo;
try {
  const res = await axios.get(API + '/v1/instagram/user/clinica_internacional', { headers });
  userInfo = res.data.user;
  console.log('PK:', userInfo.pk);
  console.log('Username:', userInfo.username);
  console.log('Full name:', userInfo.full_name);
  console.log('Followers:', userInfo.follower_count);
  console.log('Following:', userInfo.following_count);
  console.log('Bio:', userInfo.biography);
  console.log('Website:', userInfo.external_url);
  console.log('Is Business:', userInfo.is_business);
  console.log('Category:', userInfo.category);
  console.log('Email (public):', userInfo.public_email);
  console.log('Phone (public):', userInfo.public_phone_number);
  console.log('Contact phone:', userInfo.contact_phone_number);
  console.log('City:', userInfo.city_name);
} catch(e) {
  console.log('Error buscando user:', e.response ? e.response.status + ': ' + JSON.stringify(e.response.data) : e.message);
}

// ======= PASO 2: INTENTAR CREAR ANALYSIS VIA API =======
console.log('\n=== PASO 2: CREAR ANALYSIS VIA API ===');
let analysisId = null;

// Probar diferentes endpoints posibles para crear analysis
const createEndpoints = [
  '/v1/analysis/create',
  '/v1/analyses/create',
  '/v1/analysis',
  '/v1/analyses',
];

for (const ep of createEndpoints) {
  try {
    const body = {
      mode: 'followers',
      name: 'Seguidores de @clinica_internacional',
      sourceType: 'instagram',
      selectedItem: {
        pk: userInfo ? userInfo.pk : '31335673737',
        id: userInfo ? userInfo.pk : '31335673737',
        username: 'clinica_internacional',
        full_name: userInfo ? userInfo.full_name : 'Clinica Internacional',
        follower_count: userInfo ? userInfo.follower_count : 0,
        is_private: false,
        is_verified: false,
        sourceType: 'instagram',
      },
    };
    const res = await axios.post(API + ep, body, { headers });
    console.log('[' + res.status + '] POST ' + ep);
    console.log('Response:', JSON.stringify(res.data).substring(0, 500));
    if (res.data.analysisId || res.data.id) {
      analysisId = res.data.analysisId || res.data.id;
      console.log('ANALYSIS ID:', analysisId);
    }
    break;
  } catch(e) {
    const status = e.response ? e.response.status : 'ERR';
    const msg = e.response ? JSON.stringify(e.response.data).substring(0, 300) : e.message;
    console.log('[' + status + '] POST ' + ep + ' => ' + msg);
  }
}

// ======= PASO 3: INTENTAR QUEUE (si tenemos analysisId) =======
if (analysisId) {
  console.log('\n=== PASO 3: ENCOLAR ANALYSIS ===');
  try {
    const res = await axios.post(API + '/v1/queue/add-analysis', { analysisId }, { headers });
    console.log('Queue response:', JSON.stringify(res.data).substring(0, 500));
  } catch(e) {
    const msg = e.response ? JSON.stringify(e.response.data).substring(0, 300) : e.message;
    console.log('Queue error:', msg);
  }
} else {
  console.log('\n=== PASO 3: SKIP (no tenemos analysisId) ===');
  
  // Intentar queue directamente sin analysisId
  console.log('Intentando queue sin analysisId previo...');
  try {
    const res = await axios.post(API + '/v1/queue/add-analysis', {
      mode: 'followers',
      selectedItem: { pk: userInfo ? userInfo.pk : '31335673737' },
    }, { headers });
    console.log('Queue direct:', JSON.stringify(res.data).substring(0, 500));
  } catch(e) {
    const msg = e.response ? JSON.stringify(e.response.data).substring(0, 300) : e.message;
    console.log('Queue direct error:', msg);
  }
}

// ======= PASO 4: PROBAR OTROS ENDPOINTS DE ANÁLISIS =======
console.log('\n=== PASO 4: OTROS ENDPOINTS DE DATOS ===');

const dataEndpoints = [
  '/v1/analysis/list',
  '/v1/analyses/list', 
  '/v1/prospects',
  '/v1/prospects/list',
  '/v1/lists',
  '/v1/senders',
  '/v1/senders/list',
  '/v1/media/fetch?url=https://www.instagram.com/clinica_internacional/',
];

for (const ep of dataEndpoints) {
  try {
    const res = await axios.get(API + ep, { headers });
    const data = JSON.stringify(res.data).substring(0, 300);
    console.log('[' + res.status + '] GET ' + ep + ' => ' + data);
  } catch(e) {
    const status = e.response ? e.response.status : 'ERR';
    const msg = e.response ? JSON.stringify(e.response.data).substring(0, 200) : e.message;
    console.log('[' + status + '] GET ' + ep + ' => ' + msg);
  }
}

// ======= PASO 5: VERIFICAR CREDITOS DESPUES =======
console.log('\n=== PASO 5: CREDITOS DESPUES ===');
try {
  const userDoc = await getDoc(doc(db, 'users', uid));
  const data = userDoc.data();
  console.log('Plan:', data.plan);
  console.log('AI Credits:', JSON.stringify(data.aiCredits));
  console.log('Credits:', data.credits || 'no definido');
  for (const [k, v] of Object.entries(data)) {
    if (k.toLowerCase().includes('credit') || k.toLowerCase().includes('quota') || k.toLowerCase().includes('usage')) {
      console.log('  ' + k + ':', JSON.stringify(v));
    }
  }
} catch(e) { console.log('Error:', e.message); }

// ======= PASO 6: CONTAR PROSPECTS DESPUES =======
console.log('\n=== PASO 6: PROSPECTS TOTALES ===');
try {
  const snap = await getDocs(collection(db, 'users', uid, 'prospects'));
  console.log('Total prospects:', snap.size);
  let withEmail = 0;
  let withPhone = 0;
  snap.forEach(function(d) {
    const p = d.data();
    if (p.email) withEmail++;
    if (p.phone_number) withPhone++;
  });
  console.log('Con email:', withEmail);
  console.log('Con telefono:', withPhone);
} catch(e) { console.log('Error:', e.code || e.message); }

process.exit(0);
