import { State } from '../core/state.js';

/**
 * PASA v28 - Workers Dashboard: Consolidated Telemetry View
 * Single source for all workers telemetry displays
 */
export function renderWorkersView() {
    const container = document.getElementById('view-workers');
    if (!container) return;
    
    if (State.isLoading.workers && State.workers.length === 0) {
        container.innerHTML = renderWorkersLoadingSkeleton();
        return;
    }
    
    if (State.workers.length === 0) {
        container.innerHTML = renderWorkersEmptyState();
        return;
    }
    
    container.innerHTML = `
        <div class="p-5">
            <!-- Header -->
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h1 class="text-base-900 font-black text-2xl tracking-tight">
                        Sala de Máquinas
                    </h1>
                    <p class="text-base-500 text-sm">
                        Ranking de Evolução e Saúde dos Agentes PASA v28
                    </p>
                </div>
                <span class="text-xs font-bold bg-info-50 text-info-600 px-2 py-1 rounded-full">
                    ${State.workers.length} Agentes Ativos
                </span>
            </div>
            
            <!-- XP Leaderboard -->
            <div class="bg-base-100 rounded-xl border border-base-200 overflow-hidden mb-5">
                <div class="px-4 py-3 border-b border-base-200 bg-base-50">
                    <h3 class="text-xs font-black text-base-500 uppercase tracking-wider flex items-center gap-2">
                        <i data-lucide="trophy" class="w-3 h-3 text-warning-500"></i>
                        Leaderboard de Evolução
                    </h3>
                </div>
                <div class="divide-y divide-base-200">
                    ${State.workers.map((worker, index) => renderWorkerLeaderboardItem(worker, index)).join('')}
                </div>
            </div>
            
            <!-- Critical Failures -->
            <div class="bg-base-100 rounded-xl border border-base-200 overflow-hidden">
                <div class="px-4 py-3 border-b border-base-200 bg-base-50">
                    <h3 class="text-xs font-black text-base-500 uppercase tracking-wider flex items-center gap-2">
                        <i data-lucide="alert-triangle" class="w-3 h-3 text-danger-500"></i>
                        Log de Falhas Críticas
                    </h3>
                </div>
                <div class="p-4">
                    ${State.workers.some(w => w.recent_errors && w.recent_errors.length > 0) 
                        ? renderCriticalFailures() 
                        : '<p class="text-base-500 text-xs text-center py-4">Nenhuma falha registrada. Sistema estável.</p>'
                    }
                </div>
            </div>
        </div>
    `;
    
    if (window.lucide) lucide.createIcons();
}

function renderWorkerLeaderboardItem(worker, index) {
    const levelName = getLevelName(worker.current_level);
    const xpProgress = (worker.current_xp % 500) / 5; // Percentage within current level
    
    return `
        <div class="flex items-center justify-between p-4 hover:bg-base-50 transition-colors duration-200">
            <div class="flex items-center gap-4">
                <span class="text-sm font-black ${index === 0 ? 'text-warning-500' : 'text-base-400'}">
                    #${index + 1}
                </span>
                <div>
                    <p class="text-sm font-bold text-base-800">${worker.worker_id}</p>
                    <p class="text-xs text-base-500">${levelName}</p>
                </div>
            </div>
            <div class="flex items-center gap-6 text-right">
                <div>
                    <p class="text-xs font-bold text-base-800">Nível ${worker.current_level}</p>
                    <div class="w-24 bg-base-200 rounded-full h-1.5 mt-1">
                        <div class="bg-info-500 h-1.5 rounded-full" 
                             style="width: ${xpProgress}%"></div>
                    </div>
                </div>
                <span class="text-sm font-mono font-bold text-info-600 w-20 text-right">
                    ${worker.current_xp} XP
                </span>
                <span class="text-xs font-bold text-base-400 w-16">
                    ${worker.total_runs} runs
                </span>
            </div>
        </div>
    `;
}

function renderCriticalFailures() {
    const failures = State.workers
        .filter(w => w.recent_errors && w.recent_errors.length > 0)
        .flatMap(w => w.recent_errors.map(error => ({
            worker: w.worker_id,
            timestamp: error.timestamp,
            message: error.error_message || 'Erro não especificado'
        })))
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 5); // Show only top 5
    
    if (failures.length === 0) {
        return '<p class="text-base-500 text-xs text-center py-4">Nenhuma falha crítica recente.</p>';
    }
    
    return failures.map(failure => `
        <div class="flex items-start gap-3 mb-3 last:mb-0">
            <i data-lucide="x-circle" class="w-4 h-4 text-danger-500 mt-0.5 flex-shrink-0"></i>
            <div>
                <p class="text-xs font-bold text-base-700">
                    ${failure.worker} 
                    <span class="font-normal text-base-500">• ${new Date(failure.timestamp).toLocaleString()}</span>
                </p>
                <p class="text-xs text-danger-600 font-mono bg-danger-50 px-2 py-1 rounded mt-1 inline-block">
                    ${failure.message}
                </p>
            </div>
        </div>
    `).join('');
}

function renderWorkersLoadingSkeleton() {
    return `
        <div class="p-5">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h1 class="text-base-900 font-black text-2xl tracking-tight">
                        Sala de Máquinas
                    </h1>
                    <p class="text-base-500 text-sm">
                        Ranking de Evolução e Saúde dos Agentes PASA v28
                    </p>
                </div>
                <span class="text-xs font-bold bg-info-50 text-info-600 px-2 py-1 rounded-full">
                    Carregando...
                </span>
            </div>
            
            <!-- XP Leaderboard Skeleton -->
            <div class="bg-base-100 rounded-xl border border-base-200 overflow-hidden mb-5">
                <div class="px-4 py-3 border-b border-base-200 bg-base-50">
                    <h3 class="text-xs font-black text-base-500 uppercase tracking-wider flex items-center gap-2">
                        <i data-lucide="trophy" class="w-3 h-3 text-warning-500"></i>
                        Leaderboard de Evolução
                    </h3>
                </div>
                <div class="divide-y divide-base-200">
                    ${Array(3).fill(0).map(() => `
                        <div class="flex items-center justify-between p-4">
                            <div class="flex items-center gap-4">
                                <span class="text-sm font-black text-base-400">#1</span>
                                <div>
                                    <p class="text-sm font-bold text-base-800 skeleton skeleton-title w-24"></p>
                                    <p class="text-xs text-base-500 skeleton skeleton-title w-20"></p>
                                </div>
                            </div>
                            <div class="flex items-center gap-6 text-right">
                                <div>
                                    <p class="text-xs font-bold text-base-800">Nível 1</p>
                                    <div class="w-24 bg-base-200 rounded-full h-1.5 mt-1">
                                        <div class="bg-info-500 h-1.5 rounded-full" style="width: 60%"></div>
                                    </div>
                                </div>
                                <span class="text-sm font-mono font-bold text-info-600 w-20 text-right">
                                    125 XP
                                </span>
                                <span class="text-xs font-bold text-base-400 w-16">
                                    42 runs
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Critical Failures Skeleton -->
            <div class="bg-base-100 rounded-xl border border-base-200 overflow-hidden">
                <div class="px-4 py-3 border-b border-base-200 bg-base-50">
                    <h3 class="text-xs font-black text-base-500 uppercase tracking-wider flex items-center gap-2">
                        <i data-lucide="alert-triangle" class="w-3 h-3 text-danger-500"></i>
                        Log de Falhas Críticas
                    </h3>
                </div>
                <div class="p-4">
                    ${Array(3).fill(0).map(() => `
                        <div class="flex items-start gap-3 mb-3">
                            <i data-lucide="x-circle" class="w-4 h-4 text-danger-500 mt-0.5 flex-shrink-0"></i>
                            <div>
                                <p class="text-xs font-bold text-base-700 skeleton skeleton-title w-32"></p>
                                <p class="text-xs text-danger-600 font-mono bg-danger-50 px-2 py-1 rounded mt-1 inline-block skeleton skeleton-text w-full"></p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function renderWorkersEmptyState() {
    return `
        <div class="p-5 text-center">
            <i data-lucide="server-off" class="w-12 h-12 text-base-400 mx-auto mb-4"></i>
            <p class="text-base-500 text-lg">Nenhum worker encontrado</p>
            <p class="text-base-400 text-sm mt-2">
                Verifique a conexão com o sistema de monitoramento
            </p>
        </div>
    `;
}

function getLevelName(level) {
    const levelNames = {
        1: 'Recruta',
        2: 'Sentinela',
        3: 'Analista',
        4: 'Caçador',
        5: 'Mestre Forense'
    };
    return levelNames[level] || `Nível ${level}`;
}
