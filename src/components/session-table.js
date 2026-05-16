import { State, stateMutations } from '../core/state.js';
import { dataService } from '../services/dataService.js';

/**
 * PASA v47.3 - Session Management View
 * Interface para governança de contas de raspagem e rotação automática.
 */
export function renderSessionsView() {
    const container = document.getElementById('view-sessions');
    if (!container) return;

    if (State.isLoading.sessions && State.sessions.length === 0) {
        container.innerHTML = `
            <div class="p-8 flex flex-col items-center justify-center text-base-400">
                <div class="w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin mb-4"></div>
                <p>Carregando infraestrutura de sessões...</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="p-6 max-w-6xl mx-auto">
            <div class="flex items-center justify-between mb-8">
                <div>
                    <h1 class="text-2xl font-black text-base-900 tracking-tight">Governança de Contas</h1>
                    <p class="text-base-500 text-sm">Gerenciamento de sessões e rotação automática (Maestria Instagram)</p>
                </div>
                <div class="flex gap-3">
                    <button id="btn-rotate-now" class="btn btn-outline btn-sm">
                        <i data-lucide="refresh-cw" class="w-4 h-4"></i> Rotacionar Agora
                    </button>
                    <button id="btn-add-account" class="btn btn-primary btn-sm">
                        <i data-lucide="plus" class="w-4 h-4"></i> Adicionar Conta
                    </button>
                </div>
            </div>

            <!-- Dashboard de Sessões -->
            <div class="grid gap-6">
                <!-- Tabela de Sessões -->
                <div class="bg-base-100 rounded-xl border border-base-200 overflow-hidden">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-base-50 border-b border-base-200">
                                <th class="px-4 py-3 text-xs font-bold text-base-500 uppercase">Conta/ID</th>
                                <th class="px-4 py-3 text-xs font-bold text-base-500 uppercase">Status</th>
                                <th class="px-4 py-3 text-xs font-bold text-base-500 uppercase">Último Uso</th>
                                <th class="px-4 py-3 text-xs font-bold text-base-500 uppercase">Auto-Rotação</th>
                                <th class="px-4 py-3 text-xs font-bold text-base-500 uppercase">Próxima</th>
                                <th class="px-4 py-3 text-xs font-bold text-base-500 uppercase">Ações</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-base-200">
                            ${State.sessions.length > 0 ? 
                                State.sessions.map(s => renderSessionRow(s)).join('') : 
                                '<tr><td colspan="6" class="px-4 py-8 text-center text-base-400 italic">Nenhuma conta configurada. Adicione cookies para começar.</td></tr>'
                            }
                        </tbody>
                    </table>
                </div>

                <!-- Painel de Injeção (Sempre Visível) -->
                <div id="account-injection-panel" class="hidden">
                    <div class="insight-card p-6 border-2 border-primary-100 bg-primary-50/30">
                         <h3 class="font-bold text-base-900 mb-4 flex items-center gap-2">
                            <i data-lucide="key" class="w-5 h-5 text-primary-500"></i>
                            Injetar Nova Sessão de Emergência
                         </h3>
                         <div class="space-y-4">
                            <textarea id="new-account-cookies" rows="4" 
                                class="w-full p-4 rounded-lg border border-base-200 bg-base-100 text-sm font-mono focus:ring-2 focus:ring-primary-500 outline-none"
                                placeholder='Cole o JSON de cookies ou o cabeçalho "Cookie: ..." do Instagram'></textarea>
                            <div class="flex justify-end gap-3">
                                <button id="btn-cancel-injection" class="btn btn-outline btn-sm">Cancelar</button>
                                <button id="btn-confirm-injection" class="btn btn-primary btn-sm">Validar e Salvar</button>
                            </div>
                         </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Initialize Event Listeners
    setupSessionEventListeners();
    if (window.lucide) lucide.createIcons();
}

function renderSessionRow(s) {
    const isActive = s.status === 'active';
    const autoRotate = s.autoRotate || { enabled: false, intervalHours: 6, nextRotation: null };
    
    return `
        <tr class="hover:bg-base-50 transition-colors">
            <td class="px-4 py-4">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-base-200 flex items-center justify-center">
                        <i data-lucide="instagram" class="w-4 h-4 text-base-500"></i>
                    </div>
                    <div>
                        <p class="text-sm font-bold text-base-800">${s.plataforma}</p>
                        <p class="text-[10px] text-base-400 font-mono">${s.id || 'N/A'}</p>
                    </div>
                </div>
            </td>
            <td class="px-4 py-4">
                <span class="status-badge ${isActive ? 'status-badge-healthy' : 'status-badge-critical'} text-[10px]">
                    ${isActive ? 'ATIVO' : 'EXPIRADO'}
                </span>
            </td>
            <td class="px-4 py-4 text-xs text-base-500">
                ${s.updated_at ? new Date(s.updated_at).toLocaleString('pt-BR') : 'Nunca'}
            </td>
            <td class="px-4 py-4">
                <div class="flex items-center gap-3">
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" class="sr-only peer" ${autoRotate.enabled ? 'checked' : ''} 
                               onchange="window.toggleAutoRotation('${s.id}', this.checked)">
                        <div class="w-9 h-5 bg-base-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary-500"></div>
                    </label>
                    <select class="bg-transparent border-none text-[10px] font-bold text-base-600 outline-none"
                            onchange="window.updateRotationInterval('${s.id}', this.value)">
                        <option value="1" ${autoRotate.intervalHours == 1 ? 'selected' : ''}>1h</option>
                        <option value="6" ${autoRotate.intervalHours == 6 ? 'selected' : ''}>6h</option>
                        <option value="12" ${autoRotate.intervalHours == 12 ? 'selected' : ''}>12h</option>
                        <option value="24" ${autoRotate.intervalHours == 24 ? 'selected' : ''}>24h</option>
                    </select>
                </div>
            </td>
            <td class="px-4 py-4">
                <div class="flex items-center gap-1.5 text-xs ${autoRotate.enabled ? 'text-base-700' : 'text-base-300'}">
                    <i data-lucide="${autoRotate.enabled ? 'timer' : 'timer-off'}" class="w-3.5 h-3.5"></i>
                    ${autoRotate.enabled ? (autoRotate.nextRotation ? new Date(autoRotate.nextRotation).toLocaleTimeString() : 'Calculando...') : 'Manual'}
                </div>
            </td>
            <td class="px-4 py-4">
                <div class="flex gap-2">
                    <button onclick="window.deleteSession('${s.id}')" class="p-1.5 text-base-400 hover:text-danger-500 transition-colors" title="Remover Conta">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
        </tr>
    `;
}

function setupSessionEventListeners() {
    const btnAdd = document.getElementById('btn-add-account');
    const panel = document.getElementById('account-injection-panel');
    const btnCancel = document.getElementById('btn-cancel-injection');
    const btnConfirm = document.getElementById('btn-confirm-injection');
    const btnRotate = document.getElementById('btn-rotate-now');

    if (btnAdd) btnAdd.onclick = () => panel.classList.toggle('hidden');
    if (btnCancel) btnCancel.onclick = () => panel.classList.add('hidden');
    
    if (btnConfirm) {
        btnConfirm.onclick = async () => {
            const cookies = document.getElementById('new-account-cookies').value.trim();
            if (!cookies) return alert('Insira os cookies!');
            
            try {
                btnConfirm.disabled = true;
                btnConfirm.innerHTML = '<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Validando...';
                lucide.createIcons();
                
                await dataService.addSession(cookies);
                alert('Conta adicionada com sucesso!');
                window.location.reload();
            } catch (e) {
                alert('Falha ao adicionar: ' + e.message);
                btnConfirm.disabled = false;
                btnConfirm.textContent = 'Validar e Salvar';
            }
        };
    }

    if (btnRotate) {
        btnRotate.onclick = async () => {
            try {
                await dataService.rotateSession();
                alert('Rotação disparada com sucesso!');
                window.location.reload();
            } catch (e) {
                alert('Falha na rotação: ' + e.message);
            }
        };
    }

    // Global Handlers
    window.toggleAutoRotation = async (id, enabled) => {
        try {
            await dataService.updateSessionRotation(id, { enabled });
            stateMutations.updateSessionConfig(State, { id, config: { enabled } });
            // Feedback visual rápido sem reload completo
            console.log(`Auto-rotação ${enabled ? 'ativada' : 'desativada'} para ${id}`);
        } catch (e) {
            alert('Falha ao atualizar rotação: ' + e.message);
        }
    };

    window.updateRotationInterval = async (id, hours) => {
        try {
            const intervalHours = parseInt(hours);
            await dataService.updateSessionRotation(id, { intervalHours });
            stateMutations.updateSessionConfig(State, { id, config: { intervalHours } });
        } catch (e) {
            alert('Falha ao atualizar intervalo: ' + e.message);
        }
    };

    window.deleteSession = async (id) => {
        if (!confirm('Deseja realmente remover esta conta? A raspagem pode ser interrompida.')) return;
        try {
            await dataService.deleteSession(id);
            window.location.reload();
        } catch (e) {
            alert('Falha ao remover: ' + e.message);
        }
    };
}
