const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODgxMjUsImV4cCI6MjA5MjA2NDEyNX0.RMpgx8mDRrYRNfJ_GdOrsT5o8NkJiwBgW_J7CXSznWk";

const headers = {
    "apikey": SB_KEY,
    "Authorization": `Bearer ${SB_KEY}`,
    "Content-Type": "application/json"
};

export async function fetchCandidatos() {
    // Busca candidatos e garante que os campos de contagem estejam lá
    const res = await fetch(`${SB_URL}/candidatos?select=*&order=seguidores.desc`, { headers });
    if (!res.ok) throw new Error(`Fetch Candidatos Error: ${res.status}`);
    return await res.json();
}

/**
 * Busca Alertas de Ódio REAIS
 * v15.5.15 - Filtro Universal de Hostilidade
 */
export async function fetchAlertas(limit = 12) {
    // Removido filtro fixo de categoria "Odio" para aceitar qualquer categoria rotulada como ódio
    const url = `${SB_URL}/comentarios?select=*&is_hate=eq.true&order=data_coleta.desc&limit=${limit}`;
    const res = await fetch(url, { headers });
    
    if (!res.ok) throw new Error(`Fetch Alertas Error: ${res.status}`);
    
    const data = await res.json();
    console.log(`📡 Alertas brutos recebidos: ${data.length}`);
    
    return data;
}

export async function fetchComentarios(limit = 100) {
    const res = await fetch(`${SB_URL}/comentarios?select=*&limit=${limit}`, { headers });
    if (!res.ok) throw new Error(`Fetch Comentarios Error: ${res.status}`);
    return await res.json();
}
