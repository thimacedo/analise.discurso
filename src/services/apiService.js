const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
// CHAVE ANON (CORRETA PARA FRONTEND)
const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODgxMjUsImV4cCI6MjA5MjA2NDEyNX0.RMpgx8mDRrYRNfJ_GdOrsT5o8NkJiwBgW_J7CXSznWk";

const headers = {
    "apikey": SB_KEY,
    "Authorization": `Bearer ${SB_KEY}`,
    "Content-Type": "application/json"
};

export async function fetchCandidatos() {
    const res = await fetch(`${SB_URL}/candidatos?select=*&order=seguidores.desc`, { headers });
    if (!res.ok) throw new Error(`Fetch Candidatos Error: ${res.status}`);
    return await res.json();
}

export async function fetchComentarios(limit = 100) {
    const res = await fetch(`${SB_URL}/comentarios?select=*&limit=${limit}`, { headers });
    if (!res.ok) throw new Error(`Fetch Comentarios Error: ${res.status}`);
    return await res.json();
}

export async function fetchAlertas(limit = 6) {
    let url = `${SB_URL}/comentarios?select=*&is_hate=eq.true&categoria_ia=eq.Odio&order=data_coleta.desc&limit=${limit}`;
    let res = await fetch(url, { headers });
    if (!res.ok) throw new Error(`Fetch Alertas Error: ${res.status}`);
    let json = await res.json();

    // Fallback: se não houver alertas críticos (ódio), traz as últimas interações gerais
    if (!json || json.length === 0) {
        url = `${SB_URL}/comentarios?select=*&order=data_coleta.desc&limit=${limit}`;
        res = await fetch(url, { headers });
        if (!res.ok) throw new Error(`Fetch Fallback Error: ${res.status}`);
        json = await res.json();
        // Marca que são apenas interações recentes (não alertas de ódio)
        json.forEach(j => j.is_fallback = true);
    }

    return json;
}
