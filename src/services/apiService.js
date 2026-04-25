const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODgxMjUsImV4cCI6MjA5MjA2NDEyNX0.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY";

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
    // Correção: removido o join candidatos(username) que pode falhar se a FK não estiver configurada
    // e trocado criado_em por data_coleta.
    const url = `${SB_URL}/comentarios?select=*&categoria_ia=eq.Odio&order=data_coleta.desc&limit=${limit}`;
    const res = await fetch(url, { headers });
    if (!res.ok) throw new Error(`Fetch Alertas Error: ${res.status}`);
    return await res.json();
}
