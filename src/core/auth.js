/**
 * PASA v44.2 - Auth Module: Integração Supabase Auth
 * Resolve erro 404 no import do app.js
 */
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = window.SUPABASE_URL || import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = window.SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_ANON_KEY;

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
