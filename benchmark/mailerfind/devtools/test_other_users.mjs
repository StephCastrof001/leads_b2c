import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import { getFirestore, doc, getDoc, collection, getDocs } from 'firebase/firestore';

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

const cred = await signInWithEmailAndPassword(auth, 'steph@colega.lat', '20063288smcF');
const uid = cred.user.uid;
console.log('AUTH OK. My UID:', uid);

// Los related accounts del wizard tienen UIDs (id field)
// Estos son UIDs de IG (pk), NO de Firebase
// PERO el test_full_analysis.mjs intentaba leerlos como docs de Firestore
// Probemos si podemos leer docs de OTROS usuarios

// 1. Leer wizard para obtener related accounts
const userDoc = await getDoc(doc(db, 'users', uid));
const wizard = userDoc.data().wizard;
const related = wizard.relatedAccounts || [];

console.log('\n=== RELATED ACCOUNTS (10) ===');
for (const r of related) {
  console.log('  @' + r.username + ' | id: ' + r.id + ' | uid: ' + (r.uid || 'N/A') + ' | has_email: ' + r.has_email);
}

// 2. Intentar leer OTROS usuarios en Firestore usando el id como UID
console.log('\n=== INTENTAR LEER OTROS USERS EN FIRESTORE ===');
for (const r of related.slice(0, 3)) {
  const testId = r.id || r.uid;
  console.log('\n  Probando @' + r.username + ' con ID: ' + testId);
  
  // Probar como user doc
  try {
    const otherUser = await getDoc(doc(db, 'users', testId));
    if (otherUser.exists()) {
      const data = otherUser.data();
      console.log('    [users/' + testId + '] EXISTE! plan: ' + (data.plan || '-') + ', email: ' + (data.email || '-'));
      
      // Probar leer sus prospects
      try {
        const prospects = await getDocs(collection(db, 'users', testId, 'prospects'));
        console.log('    [prospects] ' + prospects.size + ' docs');
        prospects.forEach(function(d) {
          const p = d.data();
          if (p.email || p.phone_number) {
            console.log('      -> @' + p.username + ' | email: ' + (p.email || '-') + ' | phone: ' + (p.phone_number || '-'));
          }
        });
      } catch(e) { console.log('    [prospects] ERROR: ' + (e.code || e.message)); }
      
      // Probar leer sus analyses
      try {
        const analyses = await getDocs(collection(db, 'users', testId, 'analyses'));
        console.log('    [analyses] ' + analyses.size + ' docs');
      } catch(e) { console.log('    [analyses] ERROR: ' + (e.code || e.message)); }

    } else {
      console.log('    [users/' + testId + '] NO existe');
    }
  } catch(e) { console.log('    ERROR: ' + (e.code || e.message)); }
}

// 3. Probar IDs como prospects directamente (coleccion raiz?)
console.log('\n=== PROBAR COLECCIONES RAIZ ===');
const rootColls = ['prospects', 'analyses', 'analysis', 'profiles'];
for (const coll of rootColls) {
  try {
    const snap = await getDocs(collection(db, coll));
    console.log('  [' + coll + '] ' + snap.size + ' docs');
  } catch(e) { console.log('  [' + coll + '] ERROR: ' + (e.code || e.message)); }
}

process.exit(0);
