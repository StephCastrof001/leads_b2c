const firebaseConfig = {
  apiKey: "AIzaSyCLF2A2phVTJVChOcWq-lk6bOoY9hXUAGs",
  authDomain: "mailerfind-dev.firebaseapp.com",
  projectId: "mailerfind",
  storageBucket: "mailerfind.appspot.com",
  messagingSenderId: "297926607424",
  appId: "1:297926607424:web:98da15637df76fc03715a5",
  databaseURL: "https://mailerfind-default-rtdb.firebaseio.com"
};

const API = "https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI";

import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore, doc, getDoc, getDocs, collection } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const db = getFirestore(app);

console.log("=== PRUEBA RÁPIDA: 3 OTROS USUARIOS ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;

// 1. Extraer análisis propios (que funcionan)
console.log("[1] User Analysis (propios, 8 docs):");
const myAnalysis = await getDocs(collection(db, "users", uid, "analysis"));
console.log("   Total:", myAnalysis.size, "docs\n");

// 2. Extraer prospects propios (50+ docs)
console.log("[2] User Prospects (propios, 50+ docs):");
const myProspects = await getDocs(collection(db, "users", uid, "prospects"));
console.log("   Total:", myProspects.size, "docs\n");

// 3. Test: 3 usuarios relacionados del wizard
console.log("[3] Test 3 usuarios relacionados del wizard:");
const userDoc = await getDoc(doc(db, "users", uid));
const user = userDoc.data();
const wizard = user.wizard;

// Obtenemos 3 usuarios de la primera related account (si tiene uid)
const firstRelated = wizard.relatedAccounts[0]; // jugandoaprendohablar
const firstRelatedUid = firstRelated.uid || firstRelated.id;

console.log(`   First related: ${firstRelated.username} (uid: ${firstRelatedUid || 'sin uid' || 'null'})`);

if (firstRelatedUid) {
  try {
    const relatedAnalysis = await getDocs(collection(db, "users", firstRelatedUid, "analysis"));
    console.log(`   First related analysis: ${relatedAnalysis.size} docs`);
  } catch (e) {
    console.log(`   First related error: ${e.message}`);
  }
}

// 4. Test: 8 análisis propios con diferentes targets
console.log("\n[4] 8 Análisis propios con diferentes targets:");
myAnalysis.docs.forEach((doc, i) => {
  console.log(`   #${i+1}: ${doc.data().name} (${doc.data().mode})`);
});

console.log("\n=== PRUEBA COMPLETADA (Mi cuenta: 8 analyses + 50+ prospects) ===");
