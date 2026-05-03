// SENTINELA | Diamond Edition - Data Service
// Centraliza todas as chamadas para a API FastAPI

import { authService } from './authService.js';
import { state } from '../core/state.js';

const API_BASE = window.SENTINELA_CONFIG?.apiUrl || '/api/v1';

class SentinelDataService {
    constructor() {
        this.cache = new Map();
        this.cacheTTL = 60000; // 1 minuto
    }

    async fetchJson(endpoint, params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        const path = `${endpoint}${queryParams ? '?' + queryParams : ''}`;
        const cacheKey = `${API_BASE}${path}`;
        
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTTL) return cached.data;

        const tryFetch = async (baseUrl) => {
            const response = await fetch(`${baseUrl}${path}`);
            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return await response.json();
        };

        try {
            const data = await tryFetch(window.SENTINELA_CONFIG.apiUrl);
            state.lastSyncAt = new Date().toISOString();
            this.cache.set(cacheKey, { data, timestamp: Date.now() });
            return data;
        } catch (error) {
            console.warn(`[SentinelDataService] Primary path failed. Retrying fallback for ${endpoint}...`);
            try {
                return await tryFetch(window.SENTINELA_CONFIG.localFallbackUrl);
            } catch (fbError) {
                console.warn(`[SentinelDataService] All paths failed for ${endpoint}`);
                return this.getFallbackData(endpoint);
            }
        }
    }

    getFallbackData(endpoint) {
        // Dados de segurança para não deixar a UI vazia caso a API esteja offline
        const fallbacks = {
            '/summary': { total_monitorados: state.data?.length || 0, total_alertas: state.alertas?.length || 0, total_amostra: 1000, resiliencia: 98.5 },
            '/targets': [],
            '/alerts/active': [],
            '/trends': { labels: [], values: [] },
            '/networks': [],
            '/geo/uf': {}
        };
        return fallbacks[endpoint] || null;
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

    async getDossiers(candidato_id = null) {
        return this.fetchJson('/dossiers', { candidato_id });
    }

    // ── Alertas PASA ──
    async getAlerts(limit = 20, page = 1) {
        return this.fetchJson('/alerts/active', { limit, page });
    }

    async markFalsePositive(id) {
        try {
            const resp = await fetch(`${API_BASE}/alerts/false-positive`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id })
            });
            if (!resp.ok) throw new Error('Falha ao descartar alerta');
            
            // Invalida cache local para refletir a mudança no feed
            this.cache.delete(`${API_BASE}/alerts/active`);
            return await resp.json();
        } catch (e) {
            console.error('[DataService] Error marking false positive:', e);
            throw e;
        }
    }

    async fetchMoreAlertas(page = 1, limit = 20) {
        return this.getAlerts(limit, page);
    }

    // ── Redes Coordenadas ──
    async getNetworks() {
        return this.fetchJson('/networks');
    }

    // ── PASA Breakdown (Insights) ──
    async getPasaBreakdown() {
        return this.fetchJson('/pasa/breakdown');
    }

    // ── Analytics Temporal ──
    async getPasaTemporal(days = 7) {
        return this.fetchJson('/analytics/pasa-temporal', { days });
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

// Real Plan Service (Identity-Driven) - CONFIGURADO PARA MONETIZAÇÃO
export const planService = {
    getPlan: () => state.userPlan || 'free', 
    canAccess: (feature) => {
        const plan = planService.getPlan();
        if (plan === 'enterprise') return true;
        if (feature === 'identities') return plan === 'pro';
        if (feature === 'pdf_export') return false; // Sempre custa STN
        return true; // Acesso básico grátis
    },
    maskName: (name) => {
        return planService.canAccess('identities') ? name : 'Agressor Oculto';
    }
};
