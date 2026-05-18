/**
 * PASA v44.2 - Auth Module: Integração Supabase Auth
 * Resolve erro 404 no import do app.js
 */
import { getSupabase } from './supabase.js';

let currentUser = null;

export async function initAuth() {
    const supabase = getSupabase();
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
