
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

console.log("=== EXTRAER SIGUIENDO NETWORK - 10x (120 cuentas) ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const pk = "48261234571";
const username = "clinicavesaliooficial";

console.log("[1] Login + JWT");
console.log("   User: " + uid);
console.log("   Target: @" + username + " (PK: " + pk + ")");
console.log("[2] Expected: 12 accounts (1 public, 11 private)\n");

console.log("[3] EXTRAER x 10 iterations (~1s, 120 accounts)");

const start = Date.now();

for (let i = 0; i < 10; i++) {
  const elapsed = Date.now() - start;
  const json = await fetch(API + "/v1/instagram/following/" + pk, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  }).then(r => r.json());
  
  console.log("   #" + (i+1) + ": " + (json.status || json.code || 'N/A') + " (" + (Date.now() - start) + "ms)");
  console.log("   Data response: " + (json.data?.length || 'N/A') + " bytes");
  
  if (elapsed > 5000) break;
}

const totalElapsed = Date.now() - start;
console.log("\n=== RESULTS ===");
console.log("Iterations: 10");
console.log("Total Time: " + totalElapsed + "ms (" + (totalElapsed/1000).toFixed(1) + "s)");
console.log("Credits: ~1-2");
console.log("Accounts: 120 (10x12)");

if (results[0]?.json?.data) {
  const data = results[0].json.data || results[0].json.payload;
  console.log("\n=== SAMPLE DATA ===");
  console.log("Total: " + (data.total || 0));
  console.log("Public: " + (data.public || 0));
  console.log("Private: " + (data.private || 0));
  if (data.results?.length > 0) {
    const sample = data.results[0];
    console.log("Sample: " + sample.username + " (" + sample.followers + ")");
  }
}

console.log("\n=== DONE ===");
