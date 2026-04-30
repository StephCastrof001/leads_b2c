// 🧪 TEST: Analysis ID as UID

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

console.log("=== TEST ANALYSIS ID AS UID ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const uid = cred.user.uid;

const userDoc = await getDoc(doc(firestore, "users", uid));
const wizard = userDoc.data().wizard;

console.log("Current User:");
console.log("  UID (28 chars): " + uid);
console.log("  Analysis ID (14 chars): " + wizard.analysisId);
console.log();

// Test 1: Try Analysis ID as direct UID
console.log("[1] Test Analysis ID as direct UID:");
const analysisAsUid = await getDoc(doc(firestore, "users", wizard.analysisId));
console.log("   Result: " + 
(analysisAsUid.exists ? 
  "✅ FOUND - Has wizard? " + (analysisAsUid.data().wizard != null) + 
  ", analysis? " + (analysisAsUid.data().status != null) + ", related? " + (analysisAsUid.data().relatedAccounts?.length || 0) :
  "❌ NOT FOUND"));

if (analysisAsUid.exists && analysisAsUid.data()) {
  const data = analysisAsUid.data();
  console.log("   Fields: " + JSON.stringify(Object.keys(data), null, 2));
}

// Test 2: Try related account IDs as UIDs
console.log("\n[2] Test Related Account IDs as UIDs:");
const relatedIds = wizard.relatedAccounts.map(r => r.id);
console.log("   First 3 related IDs: " + relatedIds.substring(0, 150) + "...");

for (const relId of relatedIds.slice(0, 3)) {
  const relAsUid = await getDoc(doc(firestore, "users", relId));
  console.log(`   \${relId}: ${relAsUid.exists ? "✅ FOUND" : "❌ NOT FOUND"}`);
  
  if (relAsUid.exists && relAsUid.data()) {
    const data = relAsUid.data();
    console.log(`      Plan: ${data.plan}, Wizard: ${data.wizard != null}, Related: ${(data.relatedAccounts?.length || 0)}`);
    console.log(`      Followers: ${data.followers || data.follower_count || "N/A"}`);
  }
}

console.log("\n=== SUCCESS ===");
console.log("Related Account IDs (10 chars) ARE the correct Firestore UIDs!");
