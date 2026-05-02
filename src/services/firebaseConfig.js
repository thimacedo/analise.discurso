import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';
import * as admin from 'firebase-admin';
import { getApp, getApps, cert } from 'firebase-admin/app';
import dotenv from 'dotenv';

dotenv.config();

const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

// Inicializa Firebase Client-Side (Frontend)
const app = initializeApp(firebaseConfig);
export const messaging = getMessaging(app);

// Inicializa Firebase Admin (Backend)
if (!getApps().length) {
  const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT_KEY || '{}');
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

export const adminApp = admin;
