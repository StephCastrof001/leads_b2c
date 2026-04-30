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

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const pk = "48261234571";
const username = "clinicavesaliooficial";

console.log("=== EXTRAER SIGUIENDO NETWORK - 3 METHODES ===\n");

async function test(method, url, body = null) {
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
    
    console.log(method + " /" + url + ": " + (res.status || res.code || 'N/A'));
    if (res.data || res.payload) {
      console.log("  Data: " + (JSON.stringify(res.data).length || JSON.stringify(res.payload).length) + " bytes");
    }
    return res;
  } catch (e) {
    console.log(method + " /" + url + ": ERROR " + e.message);
    return null;
  }
}

console.log("[1] Testing 3 endpoints:\n");
await test("GET", "/v1/instagram/following/" + pk);
await test("POST", "/v1/instagram/following/" + pk, {pk, mode: "following"});
await test("GET", "/v1/instagram/following/" + pk, null);

console.log("\n[2] TESTING WITH USERNAME:\n");
await test("GET", "/v1/instagram/following/" + username);
await test("POST", "/v1/instagram/following/" + username, {pk, mode: "following"});
