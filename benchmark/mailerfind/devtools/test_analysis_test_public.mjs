// GET /v1/analysis/test - PRUEBA SIN JWT
// Misconfiguration: ¿Devuelve datos crudos sin autenticación?

const API = "https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI";

console.log("=== PRUEBA: GET /v1/analysis/test (SIN JWT) ===\n");

// 1. TEST 1: Sin headers
console.log("[1] GET /v1/analysis/test (sin Authorization header)");
const test1 = await fetch(API + "/v1/analysis/test").then(r => r.json());
console.log("Response:", JSON.stringify(test1, null, 2));

// 2. TEST 2: Con JWT (para comparar)
console.log("\n[2] GET /v1/analysis/test (con Firebase JWT)");
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCLF2A2phVTJVChOcWq-lk6bOoY9hXUAGs",
  authDomain: "mailerfind-dev.firebaseapp.com",
  projectId: "mailerfind",
  storageBucket: "mailerfind.appspot.com",
  messagingSenderId: "297926607424",
  appId: "1:297926607424:web:98da15637df76fc03715a5",
  databaseURL: "https://mailerfind-default-rtdb.firebaseio.com"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();

const test2 = await fetch(API + "/v1/analysis/test", {
  headers: { "Authorization": "Bearer " + token }
}).then(r => r.json());
console.log("Response:", JSON.stringify(test2, null, 2));

// 3. TEST 3: Analysis por UID (si existe endpoint)
console.log("\n[3] GET /v1/analysis/summary?uid=" + cred.user.uid);
const test3 = await fetch(API + "/v1/analysis/summary?uid=" + cred.user.uid).then(r => r.json());
console.log("Response:", JSON.stringify(test3, null, 2));

console.log("\n=== PRUEBA COMPLETADA ===");
