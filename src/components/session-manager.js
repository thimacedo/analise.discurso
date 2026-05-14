/**
 * PASA v24.1 - Injetor de Sessão de Emergência (UI)
 * Adaptado para o visual "Diamond Edition" (Tailwind + Slate)
 */
export function renderSessionManager(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="insight-card p-4 bg-white border border-slate-200 rounded-xl">
            <h3 class="text-[10px] font-black text-slate-400 uppercase mb-3 tracking-widest flex items-center gap-2">
                <i data-lucide="key-round" class="w-3 h-3 text-orange-500"></i> Injeção de Sessão IG
            </h3>
            <textarea id="ig-cookies-input" rows="3" class="w-full bg-slate-50 text-slate-700 border border-slate-200 rounded-md p-2 text-xs focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none mb-2 font-mono" placeholder="Cole os cookies de sessão aqui..."></textarea>
            <button id="inject-cookies-btn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md text-xs transition-colors flex items-center justify-center gap-2">
                <i data-lucide="zap" class="w-3 h-3"></i> INJETAR E DESPAUSAR
            </button>
            <p id="inject-status" class="text-[10px] mt-2 text-center font-medium"></p>
        </div>
    `;

    document.getElementById('inject-cookies-btn').addEventListener('click', async () => {
        const cookies = document.getElementById('ig-cookies-input').value;
        const statusEl = document.getElementById('inject-status');

        if (!cookies) {
            statusEl.textContent = '❌ Cole os cookies primeiro.';
            statusEl.className = 'text-[10px] mt-2 text-center font-medium text-red-500';
            return;
        }

        statusEl.textContent = '⏳ Enviando para a API...';
        statusEl.className = 'text-[10px] mt-2 text-center font-medium text-yellow-600';

        try {
            const res = await fetch('/api/v1/sessions/instagram/cookies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cookies })
            });

            if (res.ok) {
                statusEl.textContent = '✅ Sessão restaurada! Retomando fila...';
                statusEl.className = 'text-[10px] mt-2 text-center font-medium text-emerald-600';
                setTimeout(() => location.reload(), 2500);
            } else {
                throw new Error('Falha na resposta da API');
            }
        } catch (e) {
            statusEl.textContent = '❌ Erro crítico na injeção.';
            statusEl.className = 'text-[10px] mt-2 text-center font-medium text-red-500';
        }
    });
    
    // Renderiza ícones Lucide injetados
    if (window.lucide) lucide.createIcons();
}
