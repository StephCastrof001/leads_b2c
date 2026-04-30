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
console.log('AUTH OK. UID:', uid);

const headers = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };

async function testGet(path) {
  try {
    const res = await axios.get(API + path, { headers });
    const data = JSON.stringify(res.data).substring(0, 400);
    console.log('[' + res.status + '] GET ' + path + ' => ' + data);
  } catch (e) {
    const status = e.response ? e.response.status : 'ERR';
    const msg = JSON.stringify(e.response ? e.response.data : e.message).substring(0, 200);
    console.log('[' + status + '] GET ' + path + ' => ' + msg);
  }
}

async function testPost(path, body) {
  try {
    const res = await axios.post(API + path, body || {}, { headers });
    const data = JSON.stringify(res.data).substring(0, 400);
    console.log('[' + res.status + '] POST ' + path + ' => ' + data);
  } catch (e) {
    const status = e.response ? e.response.status : 'ERR';
    const msg = JSON.stringify(e.response ? e.response.data : e.message).substring(0, 200);
    console.log('[' + status + '] POST ' + path + ' => ' + msg);
  }
}

console.log('\n=== ENDPOINTS API (con JWT, sin gastar creditos) ===');
await testGet('/v1/pricing/plans');
await testGet('/v1/accounts');
await testGet('/v1/account-finder');
await testGet('/v1/ai/credits');
await testGet('/v1/events/active');
await testGet('/v1/milestones');
await testGet('/v1/projects');
await testGet('/v1/stripe/get-my-subscription');
await testGet('/v1/mailboxes/types');
await testGet('/v1/enrichment/presets');
await testGet('/v1/inbox');
await testGet('/v1/instagram/user/clinica_internacional');
await testPost('/v1/instagram/user/clinica_internacional');
await testGet('/v1/instagram/search-users?q=clinica');
await testGet('/v1/instagram/search-hashtags?q=dentista');
await testGet('/v1/instagram/search-places?q=lima');
await testGet('/v1/chat/conversations/main');

console.log('\n=== FIRESTORE: PROSPECTS YA EXTRAIDOS ===');
try {
  const snap = await getDocs(collection(db, 'users', uid, 'prospects'));
  console.log('Total prospects:', snap.size);
  snap.forEach(function(d) {
    const p = d.data();
    console.log('  @' + p.username + ' | email: ' + (p.email || 'null') + ' | phone: ' + (p.phone_number || 'null') + ' | website: ' + (p.website || 'null') + ' | biz: ' + p.is_business + ' | followers: ' + p.followers);
  });
} catch(e) { console.log('Prospects error:', e.code || e.message); }

console.log('\n=== FIRESTORE: ANALYSES HISTORICOS ===');
try {
  const snap = await getDocs(collection(db, 'users', uid, 'analyses'));
  console.log('Total analyses:', snap.size);
  snap.forEach(function(d) {
    const a = d.data();
    console.log('  ' + (a.name || 'unnamed') + ' | mode: ' + a.mode + ' | status: ' + a.status + ' | prospects: ' + (a.prospectsCount || 0) + ' | emailsFound: ' + (a.emailsFoundCount || 0));
  });
} catch(e) { console.log('Analyses error:', e.code || e.message); }

console.log('\n=== FIRESTORE: WIZARD RELATED ACCOUNTS (has_email?) ===');
try {
  const userDoc = await getDoc(doc(db, 'users', uid));
  const wizard = userDoc.data().wizard;
  if (wizard && wizard.relatedAccounts) {
    wizard.relatedAccounts.forEach(function(a) {
      console.log('  @' + a.username + ' | has_email: ' + a.has_email + ' | followers: ' + a.followers);
    });
  }
} catch(e) { console.log('Wizard error:', e.code || e.message); }

process.exit(0);
