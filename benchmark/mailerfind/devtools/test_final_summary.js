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
import { getFirestore, doc, getDoc, getDocs, collection } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const db = getFirestore(app);

console.log("=== PRUEBA RÁPIDA: 3 OTROS USUARIOS\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const uid = cred.user.uid;

console.log("[1] User Login:", uid);

// 2. Extraer related accounts del wizard
const userDoc = await getDoc(doc(db, "users", uid));
const user = userDoc.data();
const wizard = user.wizard;

console.log("\n[2] Wizard Data:");
console.log("   Analysis ID:", wizard.analysisId);
console.log("   Mode:", wizard.mode);
console.log("   Selected Account:", wizard.selectedAccount.username);
console.log("   Related Accounts:", wizard.relatedAccounts.length);
console.log("   Generated Emails:", wizard.generatedEmails.length);
console.log("   Business Analysis:", wizard.businessAnalysis.name);

// 3. Extraer análisis propios
console.log("\n[3] User Analysis (9 docs, PUBLIC READ):");
const myAnalysis = await getDocs(collection(db, "users", uid, "analysis"));
console.log("   Total:", myAnalysis.size, "docs");

myAnalysis.docs.forEach((doc) => {
  const d = doc.data();
  console.log(`   - ${d.name} (${d.mode || 'N/A'})`);
});

// 4. Extraer prospects propios
console.log("\n[4] User Prospects (1 doc, PUBLIC READ):");
const myProspects = await getDocs(collection(db, "users", uid, "prospects"));
console.log("   Total:", myProspects.size, "docs");

myProspects.docs.forEach((doc) => {
  const d = doc.data();
  console.log(`   - ${d.username || d.pk || 'N/A'} (${d.followers} followers)`);
});

// 5. Summary
console.log("\n[5] SUMMARY:");
console.log(`   User: ${uid}`);
console.log(`   Plan: ${user.plan}`);
console.log(`   AI Credits: ${user.aiCredits.balance}`);
console.log(`   Analysis Docs: ${myAnalysis.size}`);
console.log(`   Prospects Docs: ${myProspects.size}`);
console.log(`   Related Accounts: ${wizard.relatedAccounts.length}`);
console.log(`   Generated Emails: ${wizard.generatedEmails.length}`);
console.log(`   Business Analysis: ${wizard.businessAnalysis.name}`);

console.log("\n=== PRUEBA COMPLETADA ===");
