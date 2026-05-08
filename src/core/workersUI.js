import { state } from './state.js';
import { dataService } from '../services/dataService.js';

let pollingInterval = null;

export const workersUI = {
    async renderWorkersDashboard(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Show loading spinner initially
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center p-20 space-y-4">
                <div class="w-10 h-10 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <p class="text-slate-400 font-bold uppercase tracking-widest text-[10px]">Acessando telemetria dos workers...</p>
            </div>
        `;

        try {
            const metrics = await dataService.getWorkersMetrics();
            state.workersMetrics = metrics;

            if (!metrics) {
                container.innerHTML = `
                    <div class="p-8 text-center bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 font-bold">
                        <i data-lucide="alert-triangle" class="w-8 h-8 mx-auto mb-2 opacity-50"></i>
                        Falha ao obter telemetria. Verifique a conexão com o servidor.
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
                return;
            }

            this.drawDashboard(container, metrics);
            this.startPolling(containerId);
        } catch (error) {
            console.error('[WorkersUI] Error:', error);
            container.innerHTML = `
                <div class="p-8 text-center bg-rose-50 border border-rose-100 rounded-2xl text-rose-600 font-bold">
                    Erro fatal na renderização das métricas.
                </div>
            `;
        }
    },

    drawDashboard(container, data) {
        const healthMap = {
            'green': { color: 'text-emerald-500', bg: 'bg-emerald-500', label: 'Operacional' },
            'yellow': { color: 'text-amber-500', bg: 'bg-amber-500', label: 'Degradado' },
            'red': { color: 'text-rose-500', bg: 'bg-rose-500', label: 'Crítico' }
        };
        const health = healthMap[data.system_health] || healthMap['yellow'];
        const avgLatency = data.workers.reduce((acc, w) => acc + w.avg_duration_ms, 0) / (data.workers.length || 1);

        container.innerHTML = `
            <div class="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <!-- Header -->
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <div class="w-2 h-2 rounded-full ${health.bg} animate-pulse"></div>
                            <span class="text-[10px] font-black uppercase tracking-widest ${health.color}">System Health: ${health.label}</span>
                        </div>
                        <h2 class="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
                            Worker Dashboard
                            <span class="text-xs font-medium px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full border border-slate-200">v20.1</span>
                        </h2>
                    </div>
                    
                    <div class="flex items-center gap-4">
                        <div class="flex flex-col items-end">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Última Sincronização</span>
                            <span class="text-xs font-mono font-bold text-slate-600">${new Date(data.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <button id="refresh-workers" class="p-2.5 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all shadow-sm active:scale-95 group">
                            <i data-lucide="refresh-cw" class="w-5 h-5 text-slate-500 group-hover:rotate-180 transition-all duration-500"></i>
                        </button>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Taxa de Sucesso -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-emerald-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-emerald-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="shield-check" class="w-6 h-6 text-emerald-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Taxa de Sucesso</span>
                                <div class="text-2xl font-black text-slate-800">${data.overall_success_rate}%</div>
                            </div>
                        </div>
                        <div class="w-full h-1.5 bg-slate-50 rounded-full overflow-hidden">
                            <div class="h-full bg-emerald-500 transition-all duration-1000" style="width: ${data.overall_success_rate}%"></div>
                        </div>
                        <p class="text-[10px] text-slate-400 font-bold mt-2 uppercase">${data.total_successful} de ${data.total_executions} tarefas concluídas</p>
                    </div>

                    <!-- Latência Média -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-blue-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-blue-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="timer" class="w-6 h-6 text-blue-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Latência Média</span>
                                <div class="text-2xl font-black text-slate-800">${(avgLatency / 1000).toFixed(2)}s</div>
                            </div>
                        </div>
                        <div class="flex items-center gap-1">
                            <div class="h-1 flex-1 bg-blue-100 rounded-full"></div>
                            <div class="h-1 flex-1 bg-blue-200 rounded-full"></div>
                            <div class="h-1 flex-1 bg-blue-400 rounded-full"></div>
                            <div class="h-1 flex-1 bg-slate-100 rounded-full"></div>
                        </div>
                        <p class="text-[10px] text-slate-400 font-bold mt-2 uppercase">Tempo médio de resposta global</p>
                    </div>

                    <!-- Throughput -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-purple-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-purple-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="zap" class="w-6 h-6 text-purple-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Throughput</span>
                                <div class="text-2xl font-black text-slate-800">${data.avg_system_throughput_items_per_sec} <span class="text-xs font-normal text-slate-400">it/s</span></div>
                            </div>
                        </div>
                        <p class="text-xl font-black text-slate-800">${(data.total_items_processed / 1000).toFixed(1)}k</p>
                        <p class="text-[10px] text-slate-400 font-bold uppercase">Total de itens processados</p>
                    </div>
                </div>

                <!-- Workers Table -->
                <div class="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden">
                    <div class="px-8 py-5 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
                        <h3 class="font-black text-slate-800 uppercase tracking-widest text-xs">Processadores em Execução</h3>
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">${data.workers.length} Workers Ativos</span>
                        </div>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="bg-slate-50/50">
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Identificação</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-center">Status</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Itens Totais</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Última Atividade</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-50">
                                ${data.workers.map(w => `
                                    <tr class="hover:bg-blue-50/30 transition-colors group">
                                        <td class="px-8 py-5">
                                            <div class="flex items-center gap-3">
                                                <div class="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 font-black group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
                                                    ${w.worker.charAt(0)}
                                                </div>
                                                <div>
                                                    <div class="font-black text-slate-700 text-sm">${w.worker}</div>
                                                    <div class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">${w.success_rate}% Success Rate</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-8 py-5 text-center">
                                            <span class="px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest ${w.status === 'healthy' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-rose-100 text-rose-700 border border-rose-200'}">
                                                ${w.status}
                                            </span>
                                        </td>
                                        <td class="px-8 py-5 text-right font-mono text-xs font-black text-slate-600">
                                            ${w.total_items_processed.toLocaleString()}
                                        </td>
                                        <td class="px-8 py-5 text-right">
                                            <div class="text-xs font-black text-slate-700 font-mono">${new Date(w.last_execution.timestamp).toLocaleTimeString()}</div>
                                            <div class="text-[10px] text-slate-400 font-bold uppercase">${w.avg_duration_ms.toFixed(0)}ms avg</div>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        if (window.lucide) lucide.createIcons();
        
        // Wire up manual refresh
        const refreshBtn = document.getElementById('refresh-workers');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.renderWorkersDashboard(container.id));
        }
    },

    startPolling(containerId) {
        if (pollingInterval) clearInterval(pollingInterval);

        pollingInterval = setInterval(async () => {
            // Only poll if we are still on the workers view
            if (state.view !== 'workers') {
                clearInterval(pollingInterval);
                pollingInterval = null;
                return;
            }

            try {
                const metrics = await dataService.getWorkersMetrics();
                state.workersMetrics = metrics;
                const container = document.getElementById(containerId);
                if (container && metrics) {
                    this.drawDashboard(container, metrics);
                }
            } catch (error) {
                console.warn('[WorkersUI] Polling failed:', error);
            }
        }, 20000); // 20 seconds as requested
    }
};
