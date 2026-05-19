/**
 * PASA v28 - Sala de Máquinas: Visualização detalhada dos Workers e XP
 */

const LEVEL_NAMES = {
    1: 'Recruta',
    2: 'Sentinela',
    3: 'Analista',
    4: 'Caçador',
    5: 'Mestre Forense'
};

export async function renderWorkersView() {
    const container = document.getElementById('view-workers');
    if (!container) return;

    container.innerHTML = `<div class="flex items-center justify-center h-full"><p class="text-slate-400 text-sm">Carregando infraestrutura...</p></div>`;

    try {
        const response = await fetch('/api/v1/monitor/status');
        if (!response.ok) throw new Error('API Offline');
        const data = await response.json();

        container.innerHTML = `
            <div class="p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h1 class="text-xl font-black text-slate-800 tracking-tight">Sala de Máquinas</h1>
                        <p class="text-xs text-slate-400 font-medium">Ranking de Evolução e Saúde dos Agentes PASA v28</p>
                    </div>
                    <span class="text-[10px] font-bold bg-blue-50 text-blue-600 px-2 py-1 rounded-full">${data.worker_evolution.length} Agentes Ativos</span>
                </div>

                <!-- Leaderboard de XP -->
                <div class="bg-white rounded-xl border border-slate-200 overflow-hidden mb-8">
                    <div class="px-4 py-3 border-b border-slate-100 bg-slate-50">
                        <h3 class="text-xs font-black text-slate-500 uppercase tracking-wider flex items-center gap-2">
                            <i data-lucide="trophy" class="w-3 h-3 text-yellow-500"></i> Leaderboard de Evolução
                        </h3>
                    </div>
                    <div class="divide-y divide-slate-100">
                        ${data.worker_evolution.map((w, index) => `
                            <div class="flex items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                                <div class="flex items-center gap-4">
                                    <span class="text-sm font-black \${index === 0 ? 'text-yellow-500' : 'text-slate-400'}">#\${index + 1}</span>
                                    <div>
                                        <p class="text-sm font-bold text-slate-800">\${w.worker_id}</p>
                                        <p class="text-[10px] text-slate-500">\${LEVEL_NAMES[w.current_level] || 'Desconhecido'}</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-6 text-right">
                                    <div>
                                        <p class="text-xs font-bold text-slate-800">Nível \${w.current_level}</p>
                                        <div class="w-24 bg-slate-100 rounded-full h-1.5 mt-1">
                                            <div class="bg-blue-500 h-1.5 rounded-full" style="width: \${(w.current_xp % 500) / 5}%"></div>
                                        </div>
                                    </div>
                                    <span class="text-sm font-mono font-bold text-blue-600 w-20 text-right">\${w.current_xp} XP</span>
                                    <span class="text-[10px] font-bold text-slate-400 w-16">\${w.total_runs} runs</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Falhas Críticas Recentes -->
                <div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
                    <div class="px-4 py-3 border-b border-slate-100 bg-slate-50">
                        <h3 class="text-xs font-black text-slate-500 uppercase tracking-wider flex items-center gap-2">
                            <i data-lucide="alert-triangle" class="w-3 h-3 text-red-500"></i> Log de Falhas Críticas
                        </h3>
                    </div>
                    <div class="p-4">
                        ${data.recent_critical_failures.length === 0 ? 
                            '<p class="text-xs text-slate-400 text-center py-4">Nenhuma falha registrada. Sistema estável.</p>' :
                            data.recent_critical_failures.map(f => `
                                <div class="flex items-start gap-3 mb-3 last:mb-0">
                                    <i data-lucide="x-circle" class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0"></i>
                                    <div>
                                        <p class="text-xs font-bold text-slate-700">\${f.worker_id} <span class="font-normal text-slate-400">• \${new Date(f.created_at).toLocaleString()}</span></p>
                                        <p class="text-[10px] text-red-600 font-mono bg-red-50 px-2 py-1 rounded mt-1 inline-block">\${f.error_message || 'Erro não especificado'}</p>
                                    </div>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>
            </div>
        `;
        
        if (window.lucide) lucide.createIcons();

    } catch (e) {
        container.innerHTML = `<div class="p-6 text-center text-red-500">Falha ao carregar dados dos workers.</div>`;
    }
}
