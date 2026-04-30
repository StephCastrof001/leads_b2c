// 🧪 TEST: Verify UID Formats

const firebaseConfig = {
  apiKey: "REDACTED_API_KEY",
  authDomain: "mailerfind-dev.firebaseapp.com",
  projectId: "mailerfind",
  storageBucket: "mailerfind.appspot.com",
  messagingSenderId: "297926607424",
  appId: "1:297926607424:web:98da15637df76fc03715a5",
  databaseURL: "https://mailerfind-default-rtdb.firebaseio.com"
};

import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore, doc, getDoc } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);

console.log("=== VERIFY UID FORMATS ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const uid = cred.user.uid;
console.log("Current User UID:");
console.log("  UID: " + uid);
console.log("  Length: " + uid.length);
console.log("  Format: " + (uid.match(/^[A-Za-z0-9]+$/g) ? "ALPHANUMERIC" : "OTHER"));

const userDoc = await getDoc(doc(firestore, "users", uid));
console.log("\nCurrent User Doc:");
console.log("  Exists: " + userDoc.exists);
console.log("  Plan: " + (userDoc.data()?.plan || "N/A"));
console.log("  Wizard: " + (userDoc.data()?.wizard || "N/A"));

const wizard = userDoc.data().wizard;
console.log("\nWizard Related Accounts:");
for (let i = 0; i < Math.min(3, wizard.relatedAccounts.length); i++) {
  const rel = wizard.relatedAccounts[i];
  const uid1 = rel.uid;
  const uid2 = rel.id;
  const uid3 = rel.pbUserUid;
  
  console.log(`\n  #${i+1}. ${rel.username}:`);
  console.log(`    rel.uid: ${uid1} (len=${uid1?.length || 0})`);
  console.log(`    rel.id:  ${uid2} (len=${uid2?.length || 0})`);
  console.log(`    rel.pbUserUid: ${uid3} (len=${uid3?.length || 0})`);
  
  if (uid1) {
    const test1 = await getDoc(doc(firestore, "users", uid1));
    console.log(`    Firestore test (uid1): ${test1.exists ? "✅ FOUND" : "❌ NOT FOUND"}`);
    
    if (test1.exists && test1.data()) {
      console.log(`      Plan: ${test1.data().plan}`);
      console.log(`      Wizard: ${test1.data().wizard != null}`);
    }
  }
  
  if (uid2) {
    const test2 = await getDoc(doc(firestore, "users", uid2));
    console.log(`    Firestore test (id2): ${test2.exists ? "✅ FOUND" : "❌ NOT FOUND"}`);
  }
  
  if (uid3) {
    const test3 = await getDoc(doc(firestore, "users", uid3));
    console.log(`    Firestore test (pbUserUid): ${test3.exists ? "✅ FOUND" : "❌ NOT FOUND"}`);
  }
  console.log();
}
