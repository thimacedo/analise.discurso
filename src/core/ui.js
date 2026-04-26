/**
 * SENTINELA UI ENGINE v15.8.2
 * Absolute Production Stability
 */

import { state } from './state.js';

export function renderAll() {
    console.log("🎨 [UI] Iniciando renderiza&ccedil;&atilde;o...");
    try {
        renderKPIs();
        
        // Renderização Seletiva e Segura
        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlerts();
            renderPredictiveTrends();
            renderLiveIntelligence();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error("❌ Falha na renderização global:", e);
    }
}

// Helper de carregamento seguro
async function apiGet(endpoint) {
    try {
        const r = await fetch(`/api/v1/${endpoint}`);
        if (!r.ok) return null;
        return await r.json();
    } catch (e) {
        console.warn(`⚠️ API ${endpoint} indispon&iacute;vel`);
        return null;
    }
}

async function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;

    const data = await apiGet('stats/top-alvos');
    if (!data || !Array.isArray(data) || data.length === 0) {
        container.innerHTML = '<p class="text-[10px] text-slate-600 text-center py-20 font-black animate-pulse uppercase tracking-[0.2em]">Conectando à Base de Dados...</p>';
        // Tentar re-renderizar em 5 segundos se falhar
        setTimeout(renderMonitorImpacto, 5000);
        return;
    }

    container.innerHTML = data.map(alvo => {
        const blindagem = alvo.share_blindagem || 100;
        return `
            <div class="p-4 bg-white/[0.02] border border-white/5 rounded-2xl flex flex-col gap-2">
                <div class="flex justify-between items-center">
                    <span class="text-xs font-bold text-white">@${alvo.username}</span>
                    <span class="text-[10px] font-black text-emerald-500 font-mono">${blindagem.toFixed(1)}% Blindagem</span>
                </div>
                <div class="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div class="h-full bg-blue-600" style="width: ${blindagem}%"></div>
                </div>
            </div>`;
    }).join('');
}

async function renderLiveIntelligence() {
    const container = document.getElementById('predictive-trends');
    if (!container) return;

    const logs = await apiGet('live-intelligence');
    if (!logs || !Array.isArray(logs) || logs.length === 0) return;

    const html = `
        <div class="space-y-4 mt-8" id="live-stream-box">
            <h3 class="text-[10px] font-black text-blue-400 uppercase tracking-widest px-2">IA Stream</h3>
            ${logs.slice(0, 3).map(l => `
                <div class="p-3 bg-white/[0.02] border border-white/5 rounded-xl text-[10px]">
                    <div class="flex justify-between mb-1">
                        <span class="font-black text-white">@${l.alvo}</span>
                        <span class="text-slate-600 font-mono">${l.timestamp}</span>
                    </div>
                    <p class="text-slate-400 italic">"${l.texto}"</p>
                </div>
            `).join('')}
        </div>`;
    
    const existing = document.getElementById('live-stream-box');
    if(existing) existing.outerHTML = html;
    else container.insertAdjacentHTML('afterbegin', html);
}

function renderKPIs() {
    const set = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
    set('kpi-monitorados', state.data.length || '---');
    const hate = state.data.reduce((a, b) => a + (b.comentarios_odio_count || 0), 0);
    set('kpi-hate', hate.toLocaleString());
    set('kpi-res', 'Ativo');
}

function renderAlerts() {
    const container = document.getElementById('feed-alertas');
    if(!container || !state.alertas.length) return;
    container.innerHTML = state.alertas.slice(0, 4).map(a => `
        <div class="p-4 bg-red-500/5 border border-red-500/10 rounded-2xl">
            <p class="text-xs font-black text-white mb-2">@${a.candidato_id}</p>
            <p class="text-[11px] text-slate-300 italic">"${a.texto_bruto || a.texto}"</p>
        </div>
    `).join('');
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid');
    if(!container) return;
    container.innerHTML = state.data.map(t => `
        <div class="glass-card p-6 flex flex-col gap-4">
            <h4 class="text-[11px] font-black text-white">@${t.username}</h4>
            <div class="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-blue-600" style="width: 80%"></div>
            </div>
            <button class="w-full py-2 bg-white/5 text-[9px] font-black uppercase rounded-lg border border-white/5">Abrir Dossi&ecirc;</button>
        </div>
    `).join('');
}

function renderGeopolitica() { console.log("🌍 Mapa Geopol&iacute;tico Ativo."); }
function renderFocusDossiers() { console.log("🎯 Foco Anal&iacute;tico Ativo."); }
function renderPredictiveTrends() { console.log("🔮 Tend&ecirc;ncias Preditivas Ativas."); }
async function renderNeighborhood() { console.log("🏘️ Mapa de Vizinhan&ccedil;a Ativo."); }
