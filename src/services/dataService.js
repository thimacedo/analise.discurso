/**
 * PASA v47.1 - Data Service: Centralized API Communication
 * Single source for all data fetching with caching and error handling
 */
import { State } from '../core/state.js';
import { selectors } from '../core/state.js';
import { authService } from './authService.js';

const API_BASE = window.SENTINELA_CONFIG?.apiUrl || '/api/v1';
const CACHE_TTL = 60000; // 1 minute

class SentinelDataService {
    constructor() {
        this.cache = new Map();
    }

    /**
     * Fetch JSON data with caching and fallback
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query parameters
     * @param {Object} fetchOptions - Options for fetch (method, body, etc.)
     * @returns {Promise<any>} Parsed JSON response
     */
    async fetchJson(endpoint, params = {}, fetchOptions = {}) {
        // Build cache key
        const queryParams = new URLSearchParams(params).toString();
        const path = `${endpoint}${queryParams ? '?' + queryParams : ''}`;
        const cacheKey = `${API_BASE}${path}`;
        
        // Check cache for GET requests
        if (!fetchOptions.method || fetchOptions.method.toUpperCase() === 'GET') {
            const cached = this.cache.get(cacheKey);
            if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
                return cached.data;
            }
        }
        
        // Prepare headers
        const headers = { 
            'Content-Type': 'application/json',
            ...fetchOptions.headers
        };
        
        if (authService.isAuthenticated()) {
            headers['Authorization'] = `Bearer ${authService.session?.access_token}`;
        }
        
        // Try primary endpoint
        try {
            const response = await fetch(`${API_BASE}${path}`, { 
                ...fetchOptions,
                headers 
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            // Update cache for GET requests
            if (!fetchOptions.method || fetchOptions.method.toUpperCase() === 'GET') {
                this.cache.set(cacheKey, { data, timestamp: Date.now() });
            }
            
            return data;
        } catch (primaryError) {
            console.warn(`Primary API failed for ${endpoint}, trying fallback...`);
            
            // Try fallback endpoint (if configured)
            try {
                const fallbackResponse = await fetch(
                    `${window.SENTINELA_CONFIG?.localFallbackUrl || ''}${path}`, 
                    { ...fetchOptions, headers }
                );
                
                if (!fallbackResponse.ok) throw new Error(`HTTP ${fallbackResponse.status}`);
                
                const fallbackData = await fallbackResponse.json();
                
                // Update cache with fallback data
                if (!fetchOptions.method || fetchOptions.method.toUpperCase() === 'GET') {
                    this.cache.set(cacheKey, { data: fallbackData, timestamp: Date.now() });
                }
                
                return fallbackData;
            } catch (fallbackError) {
                console.error(`Both primary and fallback failed for ${endpoint}`, {
                    primary: primaryError,
                    fallback: fallbackError
                });
                
                // Return fallback data if available
                const fallbackData = this.getFallbackData(endpoint);
                if (fallbackData !== null) {
                    return fallbackData;
                }
                
                // Re-throw original error
                throw primaryError;
            }
        }
    }

    /**
     * Get fallback data for offline scenarios
     * @param {string} endpoint - API endpoint
     * @returns {any|null} Fallback data or null
     */
    getFallbackData(endpoint) {
        const fallbacks = {
            '/summary': {
                total_monitorados: State.data?.length || 0,
                total_alertas: State.alertas?.length || 0,
                total_amostra: 1000,
                resiliencia: 98.5
            },
            '/targets': [],
            '/alerts/active': [],
            '/trends': { labels: [], values: [] },
            '/networks': [],
            '/geo/uf': {},
            '/workers/telemetry': {
                workers: [],
                healthy_workers: 0,
                total_workers: 0
            }
        };
        
        return fallbacks[endpoint] || null;
    }

    /**
     * Invalidate cache for specific endpoint
     * @param {string} endpoint - API endpoint to invalidate
     */
    invalidateCache(endpoint) {
        const keysToDelete = [];
        for (const [key] of this.cache.entries()) {
            if (key.startsWith(`${API_BASE}${endpoint}`)) {
                keysToDelete.push(key);
            }
        }
        
        keysToDelete.forEach(key => this.cache.delete(key));
    }

    /**
     * Clear entire cache
     */
    clearCache() {
        this.cache.clear();
    }

    // ── Specific Service Methods ──
    
    async getSummary() {
        return this.fetchJson('/summary');
    }

    async getTargets(search = null, groupBy = 'score', limit = 50) {
        return this.fetchJson('/targets', { search, group_by: groupBy, limit });
    }

    async getAlerts(limit = 20, page = 1) {
        return this.fetchJson('/alerts/active', { limit, page });
    }

    async markFalsePositive(id) {
        try {
            const data = await this.fetchJson('/alerts/false-positive', { id }, {
                method: 'POST',
                body: JSON.stringify({ id })
            });
            
            // Invalidate alerts cache
            this.invalidateCache('/alerts/active');
            
            return data;
        } catch (error) {
            console.error('Failed to mark false positive:', error);
            throw error;
        }
    }

    async getWorkersTelemetry() {
        return this.fetchJson('/workers/telemetry');
    }

    async getProfilerData() {
        // Fetch from static files (no auth required)
        try {
            const [kpiResponse, streamResponse] = await Promise.all([
                fetch(`/docs/kpis.json?t=${Date.now()}`),
                fetch(`/docs/profiler_stream.json?t=${Date.now()}`)
            ]);
            
            if (!kpiResponse.ok) throw new Error(`KPIs HTTP ${kpiResponse.status}`);
            if (!streamResponse.ok) throw new Error(`Stream HTTP ${streamResponse.status}`);
            
            const [kpis, stream] = await Promise.all([
                kpiResponse.json(),
                streamResponse.json()
            ]);
            
            return {
                kpis,
                stream: stream.slice().reverse() // Most recent first
            };
        } catch (error) {
            console.error('Failed to fetch profiler data:', error);
            throw error;
        }
    }

    async getKPIs() {
        return this.fetchJson('/monitor/status');
    }
}

// Singleton instance
export const dataService = new SentinelDataService();
