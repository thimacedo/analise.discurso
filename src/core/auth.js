/**
 * PASA v44.2 - Auth Module: Integração Supabase Auth
 * Resolve erro 404 no import do app.js
 */
import { createClient } from 'https://unpkg.com/@supabase/supabase-js@2.39.7/dist/module/index.js';
import { SENTINELA_CONFIG } from '../config.js';

const supabaseUrl = SENTINELA_CONFIG.supabaseUrl;
const supabaseKey = SENTINELA_CONFIG.supabaseKey;

let supabase;
if (supabaseUrl && supabaseKey) {
    supabase = createClient(supabaseUrl, supabaseKey);
}

let currentUser = null;

export async function initAuth() {
    if (!supabase) return;
    
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
        currentUser = session.user;
    }

    supabase.auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_IN' && session) {
            currentUser = session.user;
        } else if (event === 'SIGNED_OUT') {
            currentUser = null;
        }
    });
}

export function getCurrentUserEmail() {
    return currentUser?.email || 'anonymous_user';
}
