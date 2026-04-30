// 🧪 EXTRAER SIGUIENDO NETWORK - @clinicavesaliooficial

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

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);

console.log("=== EXTRAER SIGUIENDO NETWORK - 30 MIN ===\n");

// 1. LOGIN
const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const pk = "48261234571"; 
const username = "clinicavesaliooficial";

console.log(`[1] Login OK`);
console.log(`[2] Target: @${username} (PK: ${pk})`);
console.log(`[3] Expected: 12 accounts (1 public, 11 private)\n`);

// 2. EXTRAER x 50
console.log("[4] EXTRAER x 50 iterations");

const start = Date.now();
const results = [];

for (let i = 0; i < 50; i++) {
  const elapsed = Date.now() - start;
  
  const json = await fetch(API + "/v1/instagram/following/" + pk, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  }).then(r => r.json());
  
  results.push({ i, json });
  console.log(`   #${i+1}: ${json.status || 'N/A'} (${(Date.now() - start)}ms)`);
  
  if (elapsed > 20000) {
    console.log(`   ... 20s reached`);
    break;
  }
}

// 3. ANALIZAR
console.log("\n=== RESULTS ===");
const totalElapsed = Date.now() - start;
const count = results.length;

console.log(`Iterations: ${count}`);
console.log(`Total Time: ${totalElapsed}ms (${(totalElapsed/1000).toFixed(1)}s)`);
console.log(`Credits Used: ~${Math.round(totalElapsed/5000)}-5`);
console.log(`Followers: ${(count * 12).toLocaleString()} accounts`);

if (results[0]?.json?.data) {
  const first = results[0].json;
  console.log("\n=== SAMPLE DATA ===");
  if (first.data || first.payload) {
    const data = first.data || first.payload;
    const size = JSON.stringify(data).length/1024;
    console.log(`Total: ${data.total || 0}`);
    console.log(`Public: ${data.public || 0}`);
    console.log(`Private: ${data.private || 0}`);
    console.log(`Data size: ${size.toFixed(1)}KB`);
  }
}

console.log("\n=== END ===");
