const SB_URL = 'https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1';
const SB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY';

const headers = { 'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY };

export async function fetchSyncToken() {
    try {
        // Usa o timestamp do último comentário de ódio como token de sincronização
        const r = await fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=id&order=data_coleta.desc&limit=1`, { headers });
        const data = await r.json();
        return data.length ? data[0].id : 'no_data';
    } catch (e) { return null; }
}

export async function fetchCandidatos() {
    try {
        const r = await fetch(`${SB_URL}/candidatos?select=*`, { headers });
        return r.ok ? await r.json() : [];
    } catch (e) { return []; }
}

export async function fetchAlertas(limit = 15) {
    try {
        const r = await fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=*,candidatos(username)&order=data_coleta.desc&limit=${limit}`, { headers });
        return r.ok ? await r.json() : [];
    } catch (e) { return []; }
}

export async function fetchGlobalStats() {
    try {
        const [rTotal, rHate] = await Promise.all([
            fetch(`${SB_URL}/comentarios?select=id`, { headers: { ...headers, 'Prefer': 'count=exact' }, method: 'HEAD' }),
            fetch(`${SB_URL}/comentarios?is_hate=eq.true&select=id`, { headers: { ...headers, 'Prefer': 'count=exact' }, method: 'HEAD' })
        ]);
        return { 
            total: parseInt(rTotal.headers.get('content-range')?.split('/')[1] || 0), 
            hate: parseInt(rHate.headers.get('content-range')?.split('/')[1] || 0) 
        };
    } catch (e) { return { total: 0, hate: 0 }; }
}