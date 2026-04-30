// 🧪 TEST: Find which UID format works

const firebaseConfig = {
  apiKey: "AIzaSyCLF2A2phVTJVChOcWq-lk6bOoY9hXUAGs",
  authDomain: "mailerfind-dev.firebaseapp.com",
  projectId: "mailerfind",
  storageBucket: "mailerfind.appspot.com",
  messagingSenderId: "297926607424",
  appId: "1:297926607424:web:98da15637df76fc03715a5",
  databaseURL: "https://mailerfind-default-rtdb.firebaseio.com"
};

import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore, doc, getDoc, collection, getDocs } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);

console.log("=== FIND WORKING UID ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const uid = cred.user.uid;

const userDoc = await getDoc(doc(firestore, "users", uid));
const wizard = userDoc.data().wizard;

console.log("Current User:");
console.log("  UID: " + uid);
console.log("  Analysis ID: " + wizard.analysisId);
console.log();

// Test 1: My own analysis
console.log("[1] Test My Own Analysis/Prospects:");
const myAnalysis = await getDocs(collection(firestore, "users", uid, "analysis"));
console.log("   My Analysis: " + myAnalysis.size + " docs");

const myProspects = await getDocs(collection(firestore, "users", uid, "prospects"));
console.log("   My Prospects: " + myProspects.size + " docs");

// Test 2: Related IDs that might work
console.log("\n[2] Test Related IDs (10 chars from wizard):");
const relatedIds = wizard.relatedAccounts.map(r => r.id);
console.log("   First 3 related IDs: " + relatedIds.slice(0, 3).join(", "));

for (const relId of relatedIds.slice(0, 3)) {
  // Try 3 possible paths
  const paths = [
    { path: "/users/" + relId, desc: "users/" + relId },
    { path: "/users/" + relId + "/wizard", desc: "users/" + relId + "/wizard" },
    { path: "/users/" + relId + "/analysis", desc: "users/" + relId + "/analysis" }
  ];
  
  for (const p of paths) {
    try {
      const docRef = doc(firestore, ...p.path.split("/"));
      const docSnap = await getDoc(docRef);
      console.log(`   ✅ \`${p.desc}\` = ${docSnap.data().plan || 
docSnap.data().status || 
docSnap.data().count || 
"EXISTS"} (uid=${docSnap.data().uid || docSnap.data().id || "N/A"})`);
      break;
    } catch (e) {
      // No op
    }
  }
}

// Test 3: Maybe wizard uses 28-char UIDs
console.log("\n[3] Test if Analysis ID (SpMkSYd5y0VwkIOO6ivL) works as UID?");
const wizardAnalysis = await getDoc(
  doc(firestore, "users", "SpMkSYd5y0VwkIOO6ivL", "wizard")
);
console.log("   Result: " + 
(wizardAnalysis.exists ? 
  "✅ FOUND - Data: " + 
(Object.keys(wizardAnalysis.data()) || []).join(", ") :
  "❌ NOT FOUND"));

console.log("\n=== RESULT ===");
if (wizardAnalysis.exists) {
  console.log("SUCCESS! Analysis ID IS a valid Firestore UID");
} else {
  console.log("Trying: users/" + myAnalysis.docs[0]?.data().analysisId + "/...");
}
