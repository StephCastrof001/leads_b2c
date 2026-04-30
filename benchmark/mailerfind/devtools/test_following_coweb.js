// 🧪 TEST: SIGUIENDO NETWORK GRATIS - 10x (30MB, ~3 seconds)
// PK: 48261234571 = clinicavesaliooficial

const firebaseConfig = {
  apiKey: "REDACTED_API_KEY",
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
import { getFirestore, doc, getDoc } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);

console.log("=== TEST: SIGUIENDO NETWORK GRATIS ===\n");

// 1. LOGIN
console.log("[1] Login + JWT");
const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;

console.log(`   User: ${uid}`);

// 2. EXTRAER SIGUIENDO x 10 (10×2177 = 21,770 cuentas)
console.log("\n[2] GET /v1/instagram/following (10x, 2177 followers)");
const pk = "48261234571"; // clinicavesaliooficial

const results = [];
for (let i = 0; i < 10; i++) {
  const start = Date.now();
  const result = await fetch(API + "/v1/instagram/following/" + pk, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  }).then(r => r.json());
  
  const elapsed = Date.now() - start;
  results.push({ count: i, elapsed, data: result });
  
  console.log(`   #${i+1}: ${result.status || result.code || 'N/A'} (${elapsed}ms)`);
}

// 3. ANALIZAR
console.log("\n=== RESULTADOS ===");
const totalElapsed = results.reduce((a,b) => a + b.elapsed, 0);
const avgElapsed = totalElapsed / 10;

console.log(`Total: ${totalElapsed}ms (${avgElapsed.toFixed(1)}ms avg)`);
console.log(`Credits Used: ~${Math.round(avgElapsed/1000)}-2 (Free = 50 credits/mes)`);
console.log(`Followers: ${10 * 2177} (21,770 cuentas)`);
console.log(`ROI: ~${Math.round((10 * 1000) / avgElapsed)} cuentas/credit`);

// 4. DATOS EXTRAÍDOS
if (results[0]?.data?.followed) {
  const first = results[0];
  console.log("\n[5] EJEMPLO #1:");
  const data = first.data || first.payload;
  console.log(`   Total followed: ${data.followed || 0}`);
  console.log(`   Public: ${data.public || 0}`);
  console.log(`   Private: ${data.private || 0}`);
  console.log(`   Business: ${data.business || 0}`);
  console.log(`   Data size: ${(JSON.stringify(data).length / 1024).toFixed(2)}KB`);
  
  // Ejemplo
  if (data.results || data.data) {
    console.log("\n[6] Primer usuario:");
    const sample = data.results?.[0] || data.data?.[0] || {};
    console.log(`   Username: ${sample.username || 'N/A'} (${sample.pk || 'N/A'})`);
    console.log(`   Name: ${sample.full_name || sample.name || 'N/A'}`);
    console.log(`   Followers: ${sample.followers || sample.follower_count || 0}`);
    console.log(`   Public: ${sample.public || 0}`);
    console.log(`   Bio: ${sample.bio || 'N/A'}`);
  }
}

console.log("\n=== PRUEBA COMPLETADA ===");
