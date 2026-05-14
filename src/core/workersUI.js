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
            this.renderSessionManager(container);
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
        
        // Cálculo de latência média global (ms)
        const avgLatency = data.workers.length > 0 
            ? data.workers.reduce((acc, w) => acc + (w.avg_duration_ms || 0), 0) / data.workers.length 
            : 0;

        container.innerHTML = `
            <div class="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <!-- Header -->
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <div class="w-2 h-2 rounded-full ${health.bg} animate-pulse"></div>
                            <span class="text-[10px] font-black uppercase tracking-widest ${health.color}">Saúde do Sistema: ${health.label}</span>
                        </div>
                        <h2 class="text-3xl font-black text-slate-800 tracking-tight flex items-center gap-3">
                            Workers Telemetry
                            <span class="text-xs font-medium px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full border border-slate-200">v20.2</span>
                        </h2>
                    </div>
                    
                    <div class="flex items-center gap-4">
                        <div class="flex flex-col items-end">
                            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Sincronizado em</span>
                            <span class="text-xs font-mono font-bold text-slate-600">${new Date(data.timestamp).toLocaleTimeString('pt-BR')}</span>
                        </div>
                        <button id="refresh-workers" class="p-2.5 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-all shadow-sm active:scale-95 group">
                            <i data-lucide="refresh-cw" class="w-5 h-5 text-slate-500 group-hover:rotate-180 transition-all duration-500"></i>
                        </button>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
                        <p class="text-[10px] text-slate-400 font-bold mt-2 uppercase">${data.total_successful} de ${data.total_executions} tarefas</p>
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
                            <div class="h-1 flex-1 bg-blue-500 rounded-full"></div>
                            <div class="h-1 flex-1 bg-blue-300 rounded-full"></div>
                            <div class="h-1 flex-1 bg-blue-100 rounded-full"></div>
                            <div class="h-1 flex-1 bg-slate-50 rounded-full"></div>
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
                        <p class="text-xl font-black text-slate-800">${(data.total_items_processed / 1000).toFixed(1)}k <span class="text-xs text-slate-400">itens</span></p>
                        <p class="text-[10px] text-slate-400 font-bold uppercase">Volume total processado</p>
                    </div>

                    <!-- Healthy Workers -->
                    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 hover:shadow-2xl hover:shadow-blue-100 transition-all group border-b-4 border-b-amber-500">
                        <div class="flex items-center justify-between mb-4">
                            <div class="p-3 bg-amber-50 rounded-2xl group-hover:scale-110 transition-transform">
                                <i data-lucide="activity" class="w-6 h-6 text-amber-600"></i>
                            </div>
                            <div class="text-right">
                                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Workers</span>
                                <div class="text-2xl font-black text-slate-800">${data.healthy_workers}/${data.total_workers}</div>
                            </div>
                        </div>
                        <p class="text-sm font-black text-slate-700 uppercase tracking-tighter">Instâncias Ativas</p>
                        <p class="text-[10px] text-slate-400 font-bold uppercase">Status de saúde operacional</p>
                    </div>
                </div>

                <!-- Workers Table -->
                <div class="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden">
                    <div class="px-8 py-5 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
                        <h3 class="font-black text-slate-800 uppercase tracking-widest text-xs">Processadores em Execução</h3>
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">${data.workers.length} Ativos</span>
                        </div>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left">
                            <thead>
                                <tr class="bg-slate-50/50">
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Worker</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-center">Status</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Itens</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Throughput</th>
                                    <th class="px-8 py-4 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Latência/Erros</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-50">
                                ${data.workers.map(w => {
                                    const hasErrors = w.recent_errors && w.recent_errors.length > 0;
                                    return `
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
                                            ${w.total_items_processed.toLocaleString('pt-BR')}
                                        </td>
                                        <td class="px-8 py-5 text-right">
                                            <div class="text-xs font-black text-slate-700 font-mono">${w.avg_throughput_items_per_sec || 0} it/s</div>
                                            <div class="text-[9px] text-slate-400 font-bold uppercase">Média em 24h</div>
                                        </td>
                                        <td class="px-8 py-5 text-right">
                                            <div class="text-xs font-black ${hasErrors ? 'text-rose-600' : 'text-slate-700'} font-mono">${w.avg_duration_ms.toFixed(0)}ms</div>
                                            <div class="text-[9px] ${hasErrors ? 'text-rose-400' : 'text-slate-400'} font-bold uppercase">${hasErrors ? w.recent_errors.length + ' falhas' : 'Estável'}</div>
                                        </td>
                                    </tr>
                                `;}).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Recent Errors Feed -->
                ${data.workers.some(w => w.recent_errors && w.recent_errors.length > 0) ? `
                    <div class="bg-rose-50 border border-rose-100 rounded-3xl p-6 animate-in">
                        <div class="flex items-center gap-3 mb-4">
                            <i data-lucide="alert-circle" class="w-5 h-5 text-rose-600"></i>
                            <h4 class="text-xs font-black text-rose-800 uppercase tracking-widest">Logs de Erros Críticos</h4>
                        </div>
                        <div class="space-y-3">
                            ${data.workers.filter(w => w.recent_errors && w.recent_errors.length > 0).map(w => `
                                <div class="p-4 bg-white/60 rounded-2xl border border-rose-100 text-xs border-2 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                                    <div class="flex justify-between mb-1">
                                        <span class="font-black text-rose-700 uppercase tracking-tighter">${w.worker}</span>
                                        <span class="text-slate-400 font-mono">${new Date(w.recent_errors[w.recent_errors.length-1].timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    <p class="text-slate-600 italic">"${w.recent_errors[w.recent_errors.length-1].error}"</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        if (window.lucide) lucide.createIcons();
        
        // Wire up manual refresh
        const refreshBtn = document.getElementById('refresh-workers');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.renderWorkersDashboard(container.id);
        }
    },

    async renderSessionManager(container) {
        const sessionContainer = document.createElement('div');
        sessionContainer.className = 'mt-12';
        container.appendChild(sessionContainer);

        try {
            const status = await dataService.getInstagramSessionStatus();
            
            sessionContainer.innerHTML = `
                <div class="bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50 overflow-hidden max-w-2xl">
                    <div class="px-8 py-5 border-b border-slate-50 bg-slate-800 flex items-center gap-3">
                        <i data-lucide="shield" class="text-cyan-400 w-5 h-5"></i>
                        <h3 class="font-black text-white uppercase tracking-widest text-xs">Instagram Session Manager</h3>
                    </div>
                    
                    <div class="p-8 space-y-6">
                        <div class="p-4 rounded-2xl flex items-center justify-between ${status?.status === 'active' ? 'bg-emerald-50 border border-emerald-100' : 'bg-amber-50 border border-amber-100'}">
                            <div class="flex items-center gap-3">
                                <i data-lucide="${status?.status === 'active' ? 'check-circle' : 'alert-triangle'}" class="${status?.status === 'active' ? 'text-emerald-500' : 'text-amber-500'} w-5 h-5"></i>
                                <div>
                                    <p class="text-slate-700 font-black text-xs uppercase tracking-tight">${status?.status === 'active' ? 'Sessão Ativa' : 'Sessão Ausente'}</p>
                                    <p class="text-[10px] text-slate-400 font-bold uppercase">${status?.last_updated ? 'Atualizado em: ' + new Date(status.last_updated).toLocaleString() : 'Pendente'}</p>
                                </div>
                            </div>
                        </div>

                        <form id="session-form" class="space-y-4">
                            <div class="space-y-1">
                                <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Session ID</label>
                                <input type="password" name="session_id" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition-all" placeholder="sessionid cookie value">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div class="space-y-1">
                                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">DS User ID</label>
                                    <input type="text" name="ds_user_id" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition-all" placeholder="ds_user_id">
                                </div>
                                <div class="space-y-1">
                                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">CSRF Token</label>
                                    <input type="text" name="csrf_token" required class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-5 py-3 text-sm focus:ring-2 focus:ring-cyan-500 outline-none transition-all" placeholder="csrftoken">
                                </div>
                            </div>
                            <button type="submit" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-black uppercase tracking-widest text-[10px] py-4 rounded-2xl transition-all active:scale-[0.98] shadow-lg shadow-slate-200 flex items-center justify-center gap-2">
                                <i data-lucide="save" class="w-4 h-4"></i>
                                Salvar Configurações
                            </button>
                        </form>
                    </div>
                </div>
            `;

            if (window.lucide) lucide.createIcons();

            const form = document.getElementById('session-form');
            form.onsubmit = async (e) => {
                e.preventDefault();
                const btn = e.target.querySelector('button');
                btn.disabled = true;
                btn.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4 animate-spin"></i> Salvando...';
                if (window.lucide) lucide.createIcons();

                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData.entries());
                
                try {
                    await dataService.updateInstagramSession(data);
                    alert('Sessão atualizada com sucesso!');
                    this.renderWorkersDashboard(container.id);
                } catch (err) {
                    alert('Erro ao atualizar: ' + err.message);
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = '<i data-lucide="save" class="w-4 h-4"></i> Salvar Configurações';
                    if (window.lucide) lucide.createIcons();
                }
            };

        } catch (error) {
            console.error('[WorkersUI] Session Manager Error:', error);
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
