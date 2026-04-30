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
const h = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };

// PK de clinica_internacional = 31335673737
const PK = '31335673737';
const USERNAME = 'clinica_internacional';

console.log('AUTH OK. Testing Instagram endpoints for @' + USERNAME + ' (PK: ' + PK + ')');

async function tryReq(method, path, body) {
  try {
    let res;
    if (method === 'GET') {
      res = await axios.get(API + path, { headers: h });
    } else {
      res = await axios.post(API + path, body || {}, { headers: h });
    }
    const d = JSON.stringify(res.data).substring(0, 600);
    console.log('[' + res.status + '] ' + method + ' ' + path + '\n  => ' + d);
    return res.data;
  } catch(e) {
    const s = e.response ? e.response.status : 'ERR';
    const m = e.response ? JSON.stringify(e.response.data).substring(0, 300) : e.message;
    console.log('[' + s + '] ' + method + ' ' + path + '\n  => ' + m);
    return null;
  }
}

console.log('\n========== INSTAGRAM FOLLOWERS ENDPOINTS ==========');
await tryReq('GET',  '/v1/instagram/followers/' + PK);
await tryReq('POST', '/v1/instagram/followers/' + PK);
await tryReq('POST', '/v1/instagram/followers/' + PK, { amount: 100 });
await tryReq('POST', '/v1/instagram/followers', { pk: PK, amount: 100 });
await tryReq('POST', '/v1/instagram/followers', { username: USERNAME, amount: 100 });

console.log('\n========== INSTAGRAM FOLLOWING ENDPOINTS ==========');
await tryReq('GET',  '/v1/instagram/following/' + PK);
await tryReq('POST', '/v1/instagram/following/' + PK);

console.log('\n========== INSTAGRAM COMMENTERS ENDPOINTS ==========');
await tryReq('GET',  '/v1/instagram/commenters/' + PK);
await tryReq('POST', '/v1/instagram/commenters/' + PK);

console.log('\n========== INSTAGRAM SEARCH ENDPOINTS ==========');
await tryReq('GET',  '/v1/instagram/search-users?q=clinica+dental');
await tryReq('POST', '/v1/instagram/search-users', { q: 'clinica dental' });
await tryReq('POST', '/v1/instagram/search-users', { query: 'clinica dental' });
await tryReq('GET',  '/v1/instagram/search-hashtags?q=clinicadental');
await tryReq('POST', '/v1/instagram/search-hashtags', { q: 'clinicadental' });
await tryReq('POST', '/v1/instagram/search-hashtags', { tag: 'clinicadental' });
await tryReq('GET',  '/v1/instagram/search-places?q=lima');
await tryReq('POST', '/v1/instagram/search-places', { q: 'lima' });

console.log('\n========== INSTAGRAM PROFILE VARIANTS ==========');
await tryReq('POST', '/v1/instagram/user', { username: USERNAME });
await tryReq('GET',  '/v1/instagram/user/' + USERNAME + '/followers');
await tryReq('GET',  '/v1/instagram/user/' + USERNAME + '/following');
await tryReq('GET',  '/v1/instagram/user/' + PK + '/followers');

console.log('\n========== INFLUENCER FINDER ==========');
await tryReq('GET',  '/v1/influencer-finder');
await tryReq('POST', '/v1/influencer-finder', { username: USERNAME });
await tryReq('POST', '/v1/influencer-finder', { pk: PK });
await tryReq('GET',  '/v1/influencer-finder/results');
await tryReq('GET',  '/v1/account-finder?username=' + USERNAME);
await tryReq('POST', '/v1/account-finder', { username: USERNAME });
await tryReq('POST', '/v1/account-finder', { pk: PK, mode: 'similar' });

console.log('\n========== MEDIA ENDPOINTS ==========');
await tryReq('POST', '/v1/media/fetch', { url: 'https://www.instagram.com/' + USERNAME + '/', sourceType: 'instagram' });
await tryReq('POST', '/v1/media/fetch', { username: USERNAME, sourceType: 'instagram' });

process.exit(0);
