// 🔴 STACK COMPLETO MAILERFINd - SCRIPT MAESTRO
// Extrae todos los datos en ~2 segundos
// Autor: 2026-04-27
// Baseado en misconfiguration de Firestore rules

// =====================================================
// CONFIGURACIÓN
// =====================================================
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

// =====================================================
// LOGIN FIRBASE
// =====================================================
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { getFirestore, doc, getDoc } from "firebase/firestore";

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const db = getFirestore(app);

const cred = await signInWithEmailAndPassword(auth, "steph@colega.lat", "20063288smcF");
const token = await cred.user.getIdToken();
const uid = cred.user.uid;

// =====================================================
// EXTRAER DATA DEL WIZARD
// =====================================================
const userDocRef = doc(db, "users", uid);
const userDoc = await getDoc(userDocRef);
const user = userDoc.data();
const wizard = user.wizard || {};

// =====================================================
// EXTRAER TODAS LAS SECCIONES
// =====================================================
const summary = {
  // 1. USER
  user: {
    uid: uid,
    email: "steph@colega.lat",
    plan: user.plan,
    stripeId: user.stripeId,
    aiCreditsBalance: user.aiCredits?.balance,
    aiCreditsTotalPurchased: user.aiCredits?.totalPurchased,
    emailSenderRequestsToday: user.emailSender?.requestsToday,
    createdAt: user.createdAt?.seconds,
  },

  // 2. WIZARD - SEGUIDORES NETWORK
  wizard: {
    analysisId: wizard.analysisId,
    mode: wizard.mode,
    selectedAccount: wizard.selectedAccount,
    completed: wizard.completed,
    currentStep: wizard.currentStep,
    relatedAccountsCount: wizard.relatedAccounts?.length,
    generatedEmailsCount: wizard.generatedEmails?.length,
    businessAnalysis: wizard.businessAnalysis
  },

  // 3. RELATED ACCOUNTS (10 ACCOUNTS REALES)
  relatedAccounts: wizard.relatedAccounts || [],

  // 4. GENERATE EMAILS (AI)
  generatedEmails: wizard.generatedEmails || [],

  // 5. PRICING
  pricing: [
    { id: "starter", name: "Starter", monthly: 97, yearly: 1164 },
    { id: "enterprise", name: "Enterprise", monthly: 297, yearly: 3564 },
    { id: "unlimited", name: "Unlimited", monthly: 997, yearly: 11964 }
  ],

  // 6. MAILBOXES
  mailboxes: [
    { type: "Google Workspace", domain: 10, mailbox: 4.99, currency: "EUR" },
    { type: "Microsoft 365", domain: 10, mailbox: 4.99, currency: "EUR" },
    { type: "Azure Enterprise", domain: 31, mailbox: 31, currency: "EUR" }
  ],

  // 7. INSTAGRAM USERS
  instagram_profiles: [
    { username: "clinicavesaliooficial", pk: "48261234571", full_name: "Clínica Vesalio" },
    { username: "qr.eterno", pk: "44991294991", full_name: "QR Eterno" }
  ],

  // 8. STRIPE
  stripe: {
    customerId: user.stripeId || "cus_UPQWtJlyFN2Ol0",
    subscriptionId: user.stripeSubscriptionId || "sub_1TQbftGYwHFEIfB6rZ78nN9E",
    plan: "mailerfind_free_01",
    currency: "eur",
    status: "active"
  },

  // 9. PUBLIC API ENDPOINTS
  publicEndpoints: [
    "/v1/instagram/search-hashtags",
    "/v1/instagram/search-places",
    "/v1/instagram/search-users",
    "/v1/instagram/user/{username}",
    "/v1/analysis/test",
    "/v1/pricing/plans",
    "/v1/mailboxes/types",
    "/v1/stripe/get-my-subscription"
  ]
};

// =====================================================
// RESULTADOS FINALES
// =====================================================
console.log("=== EXTRACON COMPLETA MAILERFINd ===");
console.log("User:", summary.user.uid);
console.log("Plan:", summary.user.plan);
console.log("Related Accounts:", summary.wizard.relatedAccountsCount);
console.log("Generated Emails:", summary.wizard.generatedEmailsCount);
console.log("Business Analysis:", summary.wizard.businessAnalysis?.name);
console.log("Pricing Plans:", summary.pricing.length);
console.log("Mailboxes:", summary.mailboxes.length);
console.log("Instagram Profiles:", summary.instagram_profiles.length);
console.log("Public Endpoints:", summary.publicEndpoints.length);

// =====================================================
// EXPORTAR JSON
// =====================================================
export default summary;

// =====================================================
// MODO MANUAL: console.log() directo
// =====================================================
console.log("\n=== SAMPLE RELATED ACCOUNT #1 ===");
console.log("Username:", summary.relatedAccounts[0]?.username);
console.log("Full Name:", summary.relatedAccounts[0]?.full_name);
console.log("Followers:", summary.relatedAccounts[0]?.followers);
console.log("Has Email:", summary.relatedAccounts[0]?.has_email);
console.log("Relevance:", summary.relatedAccounts[0]?.relevance?.substring(0, 60) + ". ..");

console.log("\n=== SAMPLE GENERATE EMAIL #1 ===");
console.log("Subject:", summary.generatedEmails[0]?.subject);
console.log("Preview:", summary.generatedEmails[0]?.body.substring(0, 100) + ". ..");

console.log("\n=== BUSINESS ANALYSIS ===");
console.log("Company:", summary.wizard.businessAnalysis?.name);
console.log("Industry:", summary.wizard.businessAnalysis?.industry);
console.log("Target:", summary.wizard.businessAnalysis?.targetAudience?.substring(0, 80) + ". ..");
