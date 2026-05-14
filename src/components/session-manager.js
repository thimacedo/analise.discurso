// PASA v24: Componente de Injeção de Sessão de Emergência
export function renderSessionManager(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="bg-gray-900 border border-gray-700 p-4 rounded-lg">
            <h3 class="text-sm font-bold text-gray-400 mb-2 flex items-center gap-2">
                <i data-lucide="key-round" class="w-4 h-4"></i> INJEÇÃO DE SESSÃO IG
            </h3>
            <textarea id="ig-cookies-input" rows="3" class="w-full bg-gray-800 text-gray-200 border border-gray-600 rounded p-2 text-xs focus:border-blue-500 focus:outline-none mb-2" placeholder="Cole os novos cookies aqui..."></textarea>
            <button id="inject-cookies-btn" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded text-sm transition-colors">
                INJETAR E DESPAUSAR FILA
            </button>
            <p id="inject-status" class="text-xs mt-2 text-center"></p>
        </div>
    `;

    // Re-inicializa ícones se o Lucide estiver disponível
    if (window.lucide) {
        window.lucide.createIcons();
    }

    document.getElementById('inject-cookies-btn').addEventListener('click', async () => {
        const cookies = document.getElementById('ig-cookies-input').value;
        const statusEl = document.getElementById('inject-status');

        if (!cookies) {
            statusEl.textContent = '❌ Cole os cookies primeiro.';
            statusEl.className = 'text-xs mt-2 text-center text-red-400';
            return;
        }

        statusEl.textContent = '⏳ Enviando...';
        statusEl.className = 'text-xs mt-2 text-center text-yellow-400';

        try {
            const res = await fetch('/api/v1/sessions/instagram/cookies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cookies })
            });

            if (res.ok) {
                statusEl.textContent = '✅ Sessão restaurada! Fila retomada.';
                statusEl.className = 'text-xs mt-2 text-center text-green-400';
                setTimeout(() => location.reload(), 2000); // Recarrega para limpar o alerta de CB
            } else {
                throw new Error('Falha na API');
            }
        } catch (e) {
            statusEl.textContent = '❌ Erro ao injetar sessão.';
            statusEl.className = 'text-xs mt-2 text-center text-red-400';
        }
    });
}
