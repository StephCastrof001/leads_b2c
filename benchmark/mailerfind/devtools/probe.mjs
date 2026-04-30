import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import { getFirestore, collection, addDoc, doc, getDoc, getDocs, serverTimestamp } from 'firebase/firestore';
import axios from 'axios';

const firebaseConfig = {
  apiKey: 'AIzaSyCLF2A2phVTJVChOcWq-lk6bOoY9hXUAGs',
  authDomain: 'mailerfind-dev.firebaseapp.com',
  projectId: 'mailerfind',
  storageBucket: 'mailerfind.appspot.com',
  messagingSenderId: '297926607424',
  appId: '1:297926607424:web:98da15637df76fc03715a5',
  databaseURL: 'https://mailerfind-default-rtdb.firebaseio.com'
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const API = 'https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI';

console.log('Autenticando...');
const cred = await signInWithEmailAndPassword(auth, 'steph@colega.lat', '20063288smcF');
const token = await cred.user.getIdToken();
const uid = cred.user.uid;
console.log('UID:', uid);
console.log('Token OK, len:', token.length);

// Leer user doc
const userDoc = await getDoc(doc(db, 'users', uid));
console.log('\n=== USER DOC FIELDS ===');
console.log(JSON.stringify(userDoc.data(), null, 2));

// Intentar crear analysis en users/{uid}/analyses
console.log('\n=== CREAR ANALYSIS EN users/{uid}/analyses ===');
try {
  const ref = await addDoc(collection(db, 'users', uid, 'analyses'), {
    mode: 'followers',
    status: 'PENDING',
    name: 'Seguidores de @clinicavesaliooficial',
    isCloud: true,
    sourceType: 'instagram',
    selectedItem: {
      pk: '48261234571',
      id: '48261234571',
      username: 'clinicavesaliooficial',
      full_name: 'Clinica Vesalio',
      follower_count: 2177,
      is_private: false,
      is_verified: false,
      sourceType: 'instagram'
    },
    createdAt: serverTimestamp()
  });
  console.log('CREADO ID:', ref.id);
  console.log('PATH: users/' + uid + '/analyses/' + ref.id);

  // Encolar
  const qRes = await axios.post(
    `${API}/v1/queue/add-analysis`,
    { analysisId: ref.id },
    { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }
  );
  console.log('\n=== QUEUE RESPONSE ===');
  console.log(JSON.stringify(qRes.data, null, 2));
} catch (e) {
  console.log('Error:', e.code || e.message);

  // Si falla, intentar path alternativo
  console.log('\n=== INTENTAR COLECCION RAIZ: analyses ===');
  try {
    const ref2 = await addDoc(collection(db, 'analyses'), {
      mode: 'followers',
      status: 'PENDING',
      name: 'Seguidores de @clinicavesaliooficial',
      isCloud: true,
      userId: uid,
      sourceType: 'instagram',
      selectedItem: { pk: '48261234571', username: 'clinicavesaliooficial' },
      createdAt: serverTimestamp()
    });
    console.log('CREADO EN /analyses:', ref2.id);
    const qRes2 = await axios.post(
      `${API}/v1/queue/add-analysis`,
      { analysisId: ref2.id },
      { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }
    );
    console.log('QUEUE:', JSON.stringify(qRes2.data, null, 2));
  } catch (e2) {
    console.log('Error raiz:', e2.code || e2.message);
  }
}

process.exit(0);
