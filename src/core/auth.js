/**
 * PASA v44.2 - Auth Module: Integração Supabase Auth
 * Resolve erro 404 no import do app.js
 */
const supabaseUrl = window.SENTINELA_CONFIG?.supabaseUrl;
const supabaseKey = window.SENTINELA_CONFIG?.supabaseKey;

let supabase;
if (supabaseUrl && supabaseKey && window.supabase) {
    supabase = window.supabase.createClient(supabaseUrl, supabaseKey);
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
