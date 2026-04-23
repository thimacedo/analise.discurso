const SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1";
const SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODgxMjUsImV4cCI6MjA5MjA2NDEyNX0.RMpgx8mDRrYRNfJ_GdOrsT5o8NkJiwBgW_J7CXSznWk";
const headers = { "apikey": SB_KEY, "Authorization": `Bearer ${SB_KEY}` };

export async function fetchCandidatos() {
    const res = await fetch(`${SB_URL}/candidatos?select=*&order=comentarios_totais_count.desc`, { headers });
    if (!res.ok) throw new Error(`Fetch Error: ${res.status}`);
    return await res.json();
}

export async function fetchComentarios(limit = 100) {
    const res = await fetch(`${SB_URL}/comentarios?select=categoria_ia&limit=${limit}`, { headers });
    if (!res.ok) throw new Error(`Fetch Error: ${res.status}`);
    return await res.json();
}
