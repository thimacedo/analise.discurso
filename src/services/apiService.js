const API_BASE = '/api/v1';

export async function fetchCandidatos() {
    try {
        const response = await fetch(`${API_BASE}/candidatos?t=${Date.now()}`);
        if (!response.ok) return [];
        return await response.json();
    } catch (e) {
        console.error("Erro candidatos:", e);
        return [];
    }
}

export async function fetchAlertas(limit = 10) {
    try {
        const response = await fetch(`${API_BASE}/alertas?limit=${limit}&t=${Date.now()}`);
        if (!response.ok) return [];
        return await response.json();
    } catch (e) {
        console.error("Erro alertas:", e);
        return [];
    }
}
