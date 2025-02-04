import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getAnalytics, isSupported } from 'firebase/analytics';

const firebaseConfig = {
  apiKey: "AIzaSyCaVALkjY5_8L3KRM5bnf_OB5iy5OfswYA",
  authDomain: "notes-app-bolt-45c29.firebaseapp.com",
  projectId: "notes-app-bolt-45c29",
  storageBucket: "notes-app-bolt-45c29.firebasestorage.app",
  messagingSenderId: "216396876700",
  appId: "1:216396876700:web:3c2e7df640e72d60041659",
  measurementId: "G-3X7X54HT48"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Initialize analytics only if supported
export const analytics = await isSupported().then(yes => yes ? getAnalytics(app) : null);