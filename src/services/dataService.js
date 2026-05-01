// SENTINELA | Diamond Edition - Data Service
// Centraliza todas as chamadas para a API FastAPI

import { authService } from './authService.js';

const API_BASE = window.SENTINELA_CONFIG?.apiUrl || '/api/v1';

class SentinelDataService {
    constructor() {
        this.cache = new Map();
        this.cacheTTL = 60000; // 1 minuto
    }

    async fetchJson(endpoint, params = {}) {
        const url = new URL(`${API_BASE}${endpoint}`, window.location.origin);
        Object.entries(params).forEach(([key, val]) => {
            if (val !== undefined && val !== null) url.searchParams.set(key, val);
        });

        const cacheKey = url.toString();
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
            return cached.data;
        }

        try {
            const response = await fetch(url.toString());
            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            const data = await response.json();

            this.cache.set(cacheKey, { data, timestamp: Date.now() });
            return data;
        } catch (error) {
            console.error(`[SentinelDataService] Error fetching ${endpoint}:`, error);
            throw error;
        }
    }

    // ── KPIs & Summary ──
    async getSummary() {
        return this.fetchJson('/summary');
    }

    // ── Tendências (Sparklines) ──
    async getTrends(days = 30) {
        return this.fetchJson('/trends', { days });
    }

    // ── Alvos & Dossiê ──
    async getTargets(search = null, groupBy = 'score', limit = 50) {
        return this.fetchJson('/targets', { search, group_by: groupBy, limit });
    }

    // ── Alertas PASA ──
    async getAlerts(limit = 20) {
        return this.fetchJson('/alerts/active', { limit });
    }

    // ── Redes Coordenadas ──
    async getNetworks() {
        return this.fetchJson('/networks');
    }

    // ── PASA Breakdown (Insights) ──
    async getPasaBreakdown() {
        return this.fetchJson('/pasa/breakdown');
    }

    // ── Geolocalização (Mapa) ──
    async getGeoUF() {
        return this.fetchJson('/geo/uf');
    }

    // ── Invalidação Manual de Cache ──
    invalidateCache() {
        this.cache.clear();
    }
}

// Singleton para uso em toda a aplicação
export const dataService = new SentinelDataService();

// Real Plan Service (Identity-Driven) - LIBERADO PARA TESTE
export const planService = {
    getPlan: () => 'enterprise', // Força plano máximo
    canAccess: (feature) => {
        return true; // Liberação total de funcionalidades
    },
    maskName: (name) => {
        return name; // Exibe nomes reais
    }
};
