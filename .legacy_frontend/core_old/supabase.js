/**
 * PASA v49.7 - Supabase Client Provider
 * Centraliza a inicialização do cliente para evitar múltiplas instâncias e erros de auth.
 */

let supabaseInstance = null;

export function getSupabase() {
    if (supabaseInstance) return supabaseInstance;

    const config = window.SENTINELA_CONFIG;
    if (!config || !config.supabaseUrl || !config.supabaseKey) {
        console.error('[Supabase] Configuração ausente em window.SENTINELA_CONFIG');
        return null;
    }

    if (!window.supabase) {
        console.error('[Supabase] SDK não encontrado em window.supabase. Verifique o index.html');
        return null;
    }

    supabaseInstance = window.supabase.createClient(
        config.supabaseUrl,
        config.supabaseKey
    );

    return supabaseInstance;
}
