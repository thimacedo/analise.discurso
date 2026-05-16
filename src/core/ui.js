/**
 * PASA v47.1 - UI Manager: O Construtor Visual
 * Responsabilidade única: Transformar dados do State em HTML.
 * Proteção Jurídica: NENHUMA menção a "forense", "prova" ou "evidência".
 */

export const UI = {
    renderKPIs(kpis) {
        const elements = {
            targets: document.getElementById('kpi-targets'),
            hate: document.getElementById('kpi-hate'),
            total: document.getElementById('kpi-total'),
            resilience: document.getElementById('kpi-res')
        };

        if (elements.targets) elements.targets.textContent = kpis.targets || '-';
        if (elements.hate) elements.hate.textContent = kpis.hate || '-';
        if (elements.total) elements.total.textContent = kpis.total || '-';
        if (elements.resilience) elements.resilience.textContent = `${kpis.resilience || 100}%`;
    },

    renderProfilerStream(stream) {
        const container = document.getElementById('profiler-stream-feed');
        if (!container) return;

        if (!stream || stream.length === 0) {
            container.innerHTML = '<p class="text-base-400 text-xs text-center">Aguardando dados da mineração...</p>';
            return;
        }

        container.innerHTML = stream.map(item => {
            const density = item.density || 0;
            const barColor = density > 40 ? 'bg-danger-500' : density > 10 ? 'bg-warning-500' : 'bg-success-500';
            const textColor = density > 40 ? 'text-danger-600' : density > 10 ? 'text-warning-600' : 'text-base-800';

            return `
                <div class="profiler-item">
                    <img src="/assets/sentinela_small.webp" class="profiler-avatar" onerror="this.style.display='none'">
                    <div class="profiler-info">
                        <p class="profiler-username ${textColor}">@${item.user || 'desconhecido'}</p>
                        <div class="profiler-bar-container">
                            <div class="profiler-bar ${barColor}" style="width: ${Math.min(density, 100)}%"></div>
                        </div>
                    </div>
                    <div class="profiler-stats">
                        <p class="text-xs font-black">${density}%</p>
                        <p class="text-[10px] text-base-500">${item.hate || 0}/${item.total || 0}</p>
                    </div>
                </div>
            `;
        }).join('');
    },

    renderWorkerXpRanking(workers) {
        const container = document.getElementById('worker-xp-ranking');
        if (!container) return;

        if (!workers || workers.length === 0) {
            container.innerHTML = '<p class="text-base-400 text-xs text-center">Nenhum worker detectado.</p>';
            return;
        }

        // Sort workers by XP
        const sortedWorkers = [...workers].sort((a, b) => (b.current_xp || 0) - (a.current_xp || 0));

        container.innerHTML = sortedWorkers.map((worker, index) => {
            const xp = worker.current_xp || 0;
            const level = worker.current_level || 1;
            const progress = (xp % 500) / 5; // Percentage within level

            return `
                <div class="flex items-center justify-between p-2 rounded hover:bg-base-100 transition-colors">
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-black ${index === 0 ? 'text-warning-500' : 'text-base-400'}">#${index + 1}</span>
                        <div>
                            <p class="text-xs font-bold text-base-800">${worker.worker_id}</p>
                            <p class="text-[10px] text-base-500">Nível ${level}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="text-xs font-mono font-bold text-primary-600">${xp} XP</p>
                        <div class="w-16 bg-base-200 rounded-full h-1 mt-1">
                            <div class="bg-primary-500 h-1 rounded-full" style="width: ${progress}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
};
