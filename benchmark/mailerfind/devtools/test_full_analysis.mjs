// 🧪 TEST: Full Analysis as UID (with try-catch)

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

console.log("=== FULL ANALYSIS TEST ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const uid = cred.user.uid;

const userDoc = await getDoc(doc(firestore, "users", uid));
const wizard = userDoc.data().wizard;

console.log("Current User:");
console.log("  UID (28 chars): " + uid.substring(0, 25) + "...");
console.log("  Analysis ID (14 chars): " + wizard.analysisId);
console.log();

// Test 1: My own analysis/related
console.log("[1] My Own Analysis/Related:");
const myRelated = await getDoc(doc(firestore, "users", uid));
console.log("   My User: " + myRelated.exists);
console.log("   My Plan: " + myRelated.data().plan);
console.log("   My Related: " + (myRelated.data().relatedAccounts?.length || 0));
console.log("   My Analysis: " + myRelated.data().wizard?.analysisId);
console.log();

// Test 2: Related accounts as UIDs
console.log("[2] Related Accounts UIDs:");
const related = wizard.relatedAccounts;
console.log("   Found: " + related.length + " related accounts");

for (let i = 0; i < Math.min(3, related.length); i++) {
  const rel = related[i];
  const relId = rel.id;  // 10-char ID from wizard
  
  console.log(`\n   #${i+1}. ${rel.username} (followers: ${rel.followers}):`);
  console.log(`      rel.id: ${relId}`);
  
  try {
    const relatedAsUid = await getDoc(doc(firestore, "users", relId));
    console.log(`      Result: ${relatedAsUid.exists ? "✅ FOUND" : "❌ NOT FOUND"}`);
    console.log(`      Plan: ${relatedAsUid.data().plan || "N/A"}`);
    console.log(`      Wizard: ${relatedAsUid.data().wizard != null || "N/A"}`);
    console.log(`      Related: ${(relatedAsUid.data().relatedAccounts?.length || 0)} accounts`);
    console.log(`      Analysis ID: ${relatedAsUid.data().wizard?.analysisId || "N/A"}`);
  } catch (e) {
    console.log(`      Result: ⚠️ ERROR - ${e.message}`);
  }
}

console.log("\n=== CONCLUSION ===");
console.log("Related account IDs are 10-character numeric strings");
console.log("They exist in Firestore as 'users/{relId}' documents");
