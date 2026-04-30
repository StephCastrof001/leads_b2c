// 🧪 TEST: SIGUIENDO NETWORK - 50 variants (100-500MB)

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

console.log("=== TEST: SIGUIENDO NETWORK - 5 VARIANTES ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();

const tests = [
  { url: "/v1/instagram/following/48261234571", method: "POST", type: "PK" },
  { url: "/v1/instagram/following/clinicavesaliooficial", method: "POST", type: "Username" },
  { url: "/v1/instagram/following/clinicavesaliooficial", method: "GET", type: "Username GET" },
  { url: "/v1/instagram/users/48261234571", method: "POST", type: "Users PK" },
  { url: "/v1/instagram/users/clinicavesaliooficial", method: "POST", type: "Users Username" }
];

console.log("\n=== TESTING 5 ENDPOINTS ===\n");

for (const t of tests) {
  console.log(`[${t.method} /${t.type}]`);
  
  try {
    const result = await fetch(`${API}${t.url}`, {
      method: t.method,
      headers: { 
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      }
    }).then(r => r.json());
    
    console.log(`   ${result.status || result.code || 'N/A'}`);
    
    if (result.data || result.payload || result.total) {
      console.log(`   Data: ${result.total || 10} ${result.status === 'success' ? 'ok' : ''}`);
      if (result.data?.followed) {
        console.log(`   Followed: ${result.data.followed}`);
      }
    }
  } catch (e) {
    console.log(`   Error: ${e.message}`);
  }
  
  console.log();
}

console.log("=== SUMMARY (50-100MB, 5-10s) ===");
