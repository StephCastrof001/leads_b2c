// 🧪 TEST: Extract Full Wizard Data

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
import { getFirestore, doc, getDoc } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const firestore = getFirestore(app);

console.log("=== EXTRACT FULL WIZARD DATA ===\n");

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const uid = cred.user.uid;

const userDoc = await getDoc(doc(firestore, "users", uid));
const wizard = userDoc.data().wizard;

console.log("Current User:");
console.log("  UID: " + uid);
console.log("  Plan: " + userDoc.data().plan);
console.log("  Analysis ID: " + wizard.analysisId);
console.log("  Related Accounts: " + wizard.relatedAccounts?.length || 0);
console.log();

console.log("Full Related Accounts Array:");
console.log(JSON.stringify(wizard.relatedAccounts, null, 2));
