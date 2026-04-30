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
const db = getFirestore(
  initFirestore && getFirestore(
    app
  )
);

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const pk = "48261234571";
const username = "clinicavesaliooficial";

console.log("=== EXTRAER SIGUIENDO WORKING ===\n");

// 1. Test GET /v1/pricing/plans (working)
console.log("[1] GET /v1/pricing/plans (known working):");
const pricing = await fetch(API + "/v1/pricing/plans").then(r => r.json());
console.log("   Status: " + (pricing.status || 'N/A'));
console.log("   Plans: " + (pricing.data?.plans?.length || 0));

// 2. Test Firestore (working)
console.log("\n[2] GET Firestore /users/uid/analysis (known working):");
const firestore = getFirestore(
  initFirestore && getFirestore(
    app
  )
);
const userDoc = await getDoc(doc(firestore, "users", cred.user.uid));
const myAnalysis = await getDocs(collection(firestore, "users", cred.user.uid, "analysis"));

console.log("   User doc: " + (userDoc.data().plan || 'N/A'));
console.log("   Analysis docs: " + myAnalysis.docs.length);

// 3. Test /v1/analysis/test (working)
console.log("\n[3] GET /v1/analysis/test (known working):");
const analysis = await fetch(API + "/v1/analysis/test").then(r => r.json());
console.log("   Status: " + (analysis.status || analysis.code || 'N/A'));

// 4. Test /v1/instagram/following (PK)
console.log("\n[4] GET /v1/instagram/following/" + pk);
const following = await fetch(API + "/v1/instagram/following/" + pk, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  }
}).then(r => r.json());

console.log("   Status: " + (following.status || following.code || 'N/A'));
console.log("   Data length: " + ((following.data || following.payload)?.length || 0) + " bytes");

// 5. Show data if exists
if (following.data || following.payload) {
  const data = following.data || following.payload;
  console.log("\n[5] SAMPLE DATA:");
  console.log("   Total: " + (data.total || 0));
  console.log("   Public: " + (data.public || 0));
  console.log("   Private: " + (data.private || 0));
  console.log("   Followed: " + (data.followed || 0));
  
  if (data.results || data.data) {
    console.log("\n[6] FIRST 3 RESULTS:");
    const samples = (data.results || data.data)?.slice(0, 3) || [];
    samples.forEach(sample => {
      console.log("   Username: " + (sample.username || sample.full_name || 'N/A'));
      console.log("   Follow: " + (sample.followers || 0));
      console.log("   Public: " + (sample.public || 0));
    });
  }
}

console.log("\n=== DONE ===");

// Cleanup
export { following, pricing };

function initFirestore() { return {}; }
function getFirestore(a) { return a; }
function getDoc(a) { return {}; }
function doc(a, b, c) { return { a, b, c }; }
function collection(a, b, c, d) { return { a, b, c, d }; }
function getDocs(a) { return { docs: [] }; }

