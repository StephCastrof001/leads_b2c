// EXTRAER TODOS LOS ENDPOINTS PÚBLICOS (Sin JWT)

const API = "https://us-central1-mailerfind.cloudfunctions.net/mailerfindAPI";

const endpointsTest = [
  "/v1/analysis/test",
  "/v1/pricing/plans", 
  "/v1/mailboxes/types",
  "/v1/instagram/search-hashtags",
  "/v1/instagram/search-places",
  "/v1/instagram/search-users"
];

console.log("=== PRUEBA: ENDPOINTS PÚBLICOS (Sin JWT) ===\n");

for (const endpoint of endpointsTest) {
  console.log(`[${endpoint}]`);
  
  const result = await fetch(API + endpoint).then(r => r.json());
  
  if (result.code) {
    console.log(`   Status: ${result.code} - ${result.message}`);
  } else {
    console.log(`   Success! Response:`, JSON.stringify(result, null, 2));
  }
  
  console.log();
}

// 4. TEST: Análisis con JWT (para validar misconfig)
console.log("=== TEST: ANALYSIS CON JWT (Validar misconfig) ===\n");
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore, doc, getDoc, collection, getDocs } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "REDACTED_API_KEY",
  authDomain: "mailerfind-dev.firebaseapp.com",
  projectId: "mailerfind",
  storageBucket: "mailerfind.appspot.com",
  messagingSenderId: "297926607424",
  appId: "1:297926607424:web:98da15637df76fc03715a5",
  databaseURL: "https://mailerfind-default-rtdb.firebaseio.com"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;

console.log(`User: ${uid}\n`);

// 5A. Extraer user doc
console.log("[5A] GET /users/uid (user document)");
const userDoc = await getDoc(doc(firestore, "users", uid));
console.log("   Data:", JSON.stringify({
  plan: userDoc.data().plan,
  aiCredits: userDoc.data().aiCredits.balance,
  wizard: !!userDoc.data().wizard,
}) );

// 5B. Extraer analysis subcollection
console.log("\n[5B] GET /users/uid/analysis (analysis subcollection)");
const analysisColl = collection(firestore, "users", uid, "analysis");
const analysisDocs = await getDocs(analysisColl);
console.log("   Total:", analysisDocs.size, "docs");

analysisDocs.docs.forEach((doc, i) => {
  const d = doc.data();
  console.log(`   #${i+1}: ${d.name || 'N/A'} (${d.mode || 'N/A'})`);
});

// 5C. Extraer prospects subcollection
console.log("\n[5C] GET /users/uid/prospects (prospects subcollection)");
const prospectsColl = collection(firestore, "users", uid, "prospects");
const prospectsDocs = await getDocs(prospectsColl);
console.log("   Total:", prospectsDocs.size, "docs");

prospectsDocs.docs.forEach((doc, i) => {
  const d = doc.data();
  console.log(`   #${i+1}: ${d.username || d.pk || 'N/A'} (${d.followers} followers)`);
});

console.log("\n=== PRUEBA COMPLETADA ===");
export default { endpointsTest, user, analysisDocs, prospectsDocs };
