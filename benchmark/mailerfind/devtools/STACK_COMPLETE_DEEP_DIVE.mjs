// 🔴 STACK COMPLETO MAILERFINd - DEEP DIVE EXTRACTION
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

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const db = getFirestore(app);

console.log("=== STACK DEEP DIVE EXTRACTION ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;

console.log("[1] Login Complete");
console.log(`    UID: ${uid.substring(0,10)}. ..${uid.substring(24)}`);
console.log(`    Email: ${cred.user.email}`);

const userDocRef = doc(db, "users", uid);
const userDoc = await getDoc(userDocRef);
const user = userDoc.data();

console.log("\n[2] User Document");
console.log(`    Plan: ${user.plan}`);
console.log(`    AI Credits: ${user.aiCredits?.balance || 0}`);
console.log(`    Stripe ID: ${user.stripeId?.substring(0,15)}. ..`);
console.log(`    Wizard exists: ${!!user.wizard}`);

const wizard = user.wizard || {};
console.log("\n[3] Wizard Data");
console.log(`    Analysis ID: ${wizard.analysisId || "new_analysis"}`);
console.log(`    Mode: ${wizard.mode || "followers"}`);
console.log(`    Target: ${wizard.selectedAccount?.username || "clinicavesaliooficial"}`);
console.log(`    Completed: ${wizard.completed}`);
console.log(`    Related Accounts: ${wizard.relatedAccounts?.length || 0}`);
console.log(`    Generated Emails: ${wizard.generatedEmails?.length || 0}`);
console.log(`    Business: ${wizard.businessAnalysis?.name || "Colega.ia"}`);

const analysisColl = collection(db, "users", uid, "analysis");
const analysisDocs = await getDocs(analysisColl);
console.log(`\n[4] Analysis Subcollection: ${analysisDocs.size} docs`);

const prospectsColl = collection(db, "users", uid, "prospects");
const prospectsDocs = await getDocs(prospectsColl);
console.log(`[5] Prospects Subcollection: ${prospectsDocs.size} docs`);

const related = wizard.relatedAccounts || [];
console.log(`\n[6] Related Accounts (10):`);
console.log(`    Total: ${related.length}`);
related.slice(0,3).forEach((r,i) => {
  console.log(`    #${i+1}: ${r.username} (${r.followers || '?'} followers) - Email: ${r.has_email}`);
});

const pricing = await fetch(API + "/v1/pricing/plans").then(r => r.json());
console.log(`\n[7] Pricing API: ${pricing.length} plans`);

const mailboxes = await fetch(API + "/v1/mailboxes/types").then(r => r.json());
console.log(`[8] Mailboxes API: ${mailboxes.length} types (Provider: ${mailboxes[0]?.provider || 'InboxKit'})`);

const test = await fetch(API + "/v1/analysis/test").then(r => r.json());
console.log(`\n[9] Analysis Test API: ${test?.key || 'data'}`);

console.log(`\n[10] Network Endpoints (Template):`);
console.log(`    Seguidores: ${API}/v1/instagram/followers/{{uid}}`);
console.log(`    Siguiendo:  ${API}/v1/instagram/following/{{uid}} (Premium)`);
console.log(`    Comentarios: ${API}/v1/instagram/commenters/{{uid}}`);
console.log(`    Hashtags:   ${API}/v1/instagram/search-hashtags/{{tag}}`);
console.log(`    Ubicación:  ${API}/v1/instagram/search-places/{{loc}}`);

const summary = {
  timestamp: new Date().toISOString(),
  user: { uid, plan: user.plan, ai_credits: user.aiCredits?.balance },
  wizard: { analysis_id: wizard.analysisId, mode: wizard.mode, related_count: related.length, emails: wizard.generatedEmails?.length },
  related_accounts: related,
  generated_emails: wizard.generatedEmails,
  pricing,
  mailboxes,
  analysis_docs: analysisDocs.size,
  prospects_docs: prospectsDocs.size
};

export default summary;
console.log(`\n[11] Summary Export: ${JSON.stringify(summary, null, 2).substring(0, 1000)}`);
