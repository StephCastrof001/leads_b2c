// 🧪 TEST: SCALE 3 RELATED PROFILES (2 min, 3 related accounts)
// Corrected: Using Firebase UID from wizard.relatedAccounts

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
import { getFirestore, doc, getDoc, getDocs, collection } from "firebase/firestore";

// Initialize
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);

console.log("=== TEST: SCALE 3 RELATED PROFILES ===\n");

// 1. Login + Get Wizard
console.log("[1] Login + Get User Wizard");
const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;

console.log(`   User UID: ${uid}`);

const userDoc = await getDoc(doc(firestore, "users", uid));
const wizard = userDoc.data().wizard;

console.log(`   Analysis ID: ${wizard.analysisId}`);
console.log(`   Related Accounts Count: ${wizard.relatedAccounts?.length || 0}`);

if (!wizard.relatedAccounts || wizard.relatedAccounts.length < 3) {
  console.log("Warning: Less than 3 related accounts found");
}

// 2. Scale 3 Related Profiles
console.log("\n[2] EXTRAER 3 RELATED PROFILES:");
const relatedSamples = [];

for (let i = 0; i < Math.min(3, wizard.relatedAccounts.length); i++) {
  const related = wizard.relatedAccounts[i];
  const relatedUid = related.uid || related.id;
  const username = related.username || "N/A";
  
  console.log(`\n   #${i+1}. ${username} (UID: ${relatedUid?.substring(0, 8)}...${relatedUid?.substring(relatedUid.length - 4)})`);
  
  // Verify user doc exists
  try {
    const relatedUserDoc = await getDoc(doc(firestore, "users", relatedUid));
    console.log(`      ✅ User Doc: ${relatedUserDoc.exists()}`);
    
    // Extract analysis
    const analysisColl = collection(firestore, "users", relatedUid, "analysis");
    const analysisDocs = await getDocs(analysisColl);
    console.log(`      ✅ Analysis: ${analysisDocs.size} docs`);
    
    // Extract prospects
    const prospectsColl = collection(firestore, "users", relatedUid, "prospects");
    const prospectsDocs = await getDocs(prospectsColl);
    console.log(`      ✅ Prospects: ${prospectsDocs.size} docs`);
    
    // Extract wizard data
    const wizardSample = {
      username: related.username,
      uid: relatedUid,
      followers: related.followers || related.follower_count || 0,
      followerCount: related.following || 0,
      isPrivate: related.is_private || false,
      isBusiness: related.is_business || false,
      verified: related.is_verified || false,
      analysisCount: analysisDocs.size,
      prospectsCount: prospectsDocs.size
    };
    
    relatedSamples.push(wizardSample);
  } catch (e) {
    console.log(`      ✗ Error: ${e.message}`);
  }
}

// 3. Summary
console.log("\n=== SUMMARY ===");
const totalDocs = relatedSamples.reduce((sum, s) => sum + s.analysisCount + s.prospectsCount, 0);
const totalFollowers = relatedSamples.reduce((sum, s) => sum + s.followers, 0);
const publicCount = relatedSamples.filter(s => !s.isPrivate).length;
const businessCount = relatedSamples.filter(s => s.isBusiness).length;

console.log(`Total Related: ${relatedSamples.length}`);
console.log(`Total Analysis Docs: ${totalDocs}`);
console.log(`Total Followers: ${totalFollowers.toLocaleString()}`);
console.log(`Public Accounts: ${publicCount}/${relatedSamples.length}`);
console.log(`Business Accounts: ${businessCount}/${relatedSamples.length}`);
console.log("\nEstimated Data Size:");
console.log(`   Analysis: ${totalDocs * 10}MB = ${(totalDocs * 10 / (1024*1024)).toFixed(2)}MB`);
console.log(`   Prospects: ${totalDocs * 20}MB = ${(totalDocs * 20 / (1024*1024)).toFixed(2)}MB`);
console.log(`   Total: ~${(totalDocs * 30 / (1024*1024)).toFixed(2)}MB (${totalDocs.toLocaleString()} docs)`);

// 4. Sample Data
console.log("\n=== SAMPLE DATA (First Related) ===");
if (relatedSamples[0]) {
  const sample = relatedSamples[0];
  console.log("Username: " + sample.username);
  console.log("Followers: " + sample.followers.toLocaleString());
  console.log("Is Public: " + sample.isPrivate ? 'NO (Private)' : 'YES');
  console.log("Is Business: " + sample.isBusiness ? 'YES' : 'NO');
  console.log("Analysis Docs: " + sample.analysisCount);
  console.log("Prospects Docs: " + sample.prospectsCount);
  
  // Get first analysis name
  if (sample.analysisCount > 0) {
    const firstAnalysis = analysisDocs.docs[0];
    const analysisData = firstAnalysis.data();
    console.log("First Analysis Name: " + (analysisData.name || "N/A"));
    console.log("First Analysis Mode: " + (analysisData.mode || "N/A"));
    console.log("First Analysis Status: " + (analysisData.status || "N/A"));
  }
}

console.log("\n=== END ===");
