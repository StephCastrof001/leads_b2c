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

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;
const pk = "48261234571";
const username = "clinicavesaliooficial";

console.log("=== EXTRAER SIGUIENDO NETWORK - 10x (120 cuentas) ===\n");
console.log("[1] Login + JWT");
console.log("   User: " + uid);
console.log("   Target: @" + username + " (PK: " + pk + ")");
console.log("   Expected: 12 accounts (1 public, 11 private)\n");

console.log("[2] EXTRAER x 10 iterations (~1s, 120 accounts)");

const start = Date.now();
const results = [];

for (let i = 0; i < 10; i++) {
  const elapsed = Date.now() - start;
  const json = await fetch(API + "/v1/instagram/following/" + pk, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    }
  }).then(r => r.json());
  
  results.push(json);
  console.log("   #" + (i+1) + ": " + (json.status || json.code || 'N/A') + " (" + ((Date.now() - start)/1000).toFixed(1) + "s)");
  
  if (elapsed > 5000) break;
}

const totalElapsed = Date.now() - start;

console.log("\n=== RESULTS ===");
console.log("Iterations: " + results.length);
console.log("Total Time: " + totalElapsed + "ms (" + (totalElapsed/1000).toFixed(1) + "s)");
console.log("Credits: ~1-2");
console.log("Accounts: " + (results.length * 12));

if (results[0].data || results[0].payload) {
  const firstData = results[0].data || results[0].payload;
  console.log("\n=== SAMPLE DATA (First call) ===");
  console.log("Total: " + (firstData.total || 0));
  console.log("Public: " + (firstData.public || 0));
  console.log("Private: " + (firstData.private || 0));
  console.log("Results length: " + (firstData.results?.length || 0));
  
  if (firstData.results?.length > 0) {
    console.log("\n=== SAMPLE USER #1 ===");
    const sample = firstData.results[0];
    console.log("Username: " + (sample.username || sample.pk || "N/A"));
    console.log("Followers: " + (sample.followers || 0));
    console.log("Public: " + (sample.public || 0));
    console.log("Data Size: " + (JSON.stringify(firstData).length/1024).toFixed(2) + "KB");
  }
}

console.log("\n=== END ===");
