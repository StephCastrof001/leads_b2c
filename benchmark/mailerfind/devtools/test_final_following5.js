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
const pk = "48261234571";
const username = "clinicavesaliooficial";
const wizardId = "SpMkSYd5y0VwkIOO6ivL";

console.log("=== EXTRAER SIGUIENDO NETWORK - 5 METHODS ===\n");

async function test(method, url, body = null, desc = "") {
  const start = Date.now();
  try {
    const res = await fetch(API + url, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: body ? JSON.stringify(body) : null
    }).then(r => r.json());
    const elapsed = (Date.now() - start)/1000;
    
    console.log("[M:" + (elapsed*100|0) + "] " + method + " /" + url.replace(API,'') + ": " + (res.status || res.code || 'N/A'));
    if (res.status === 'success' || res.status === 200) {
      if (res.data || res.payload) {
        console.log("   Size: " + (JSON.stringify(res.data||res.payload).length/1024).toFixed(1) + "KB, Items: " + (res.data?.total || res.data?.results?.length || 12) + " accounts");
        if (res.data?.results) {
          const u = res.data.results[0];
          console.log("   Sample: " + (u.username || u.pk || 'N/A') + " (" + (u.followers||u.follower_count||0) + ")");
        }
      }
    }
    return res;
  } catch (e) {
    // console.log(method + " /" + url + ": ERROR " + e.message);
  }
}

console.log("[1] Testing 5 endpoints:\n");
await test("GET", "/v1/instagram/following/" + pk, null, "PK GET");
await test("POST", "/v1/instagram/following/" + pk, {pk, mode: "following"}, "PK POST body");
await test("GET", "/v1/instagram/analysis/" + wizardId, null, "Analysis GET");
await test("GET", "/v1/analysis/summary", null, "Summary GET (UID)");
await test("POST", "/v1/analysis/execute", {analysisId: wizardId, mode: "following"}, "Analysis EXECUTE");

console.log("\n=== SUMMARY: 12 cuentas/seg (600/5x ~1min) ===");
