/**
 * Sentinela API Service
 * v15.11.0 - Robust Fetching
 */

export async function fetchCandidatos() {
    try {
        const response = await fetch('/api/v1/stats/top-alvos');
        if (!response.ok) return [];
        return await response.json();
    } catch { return []; }
}

export async function fetchAlertas(limit = 10) {
    // Implementação básica de retorno de alertas
    return [];
}
