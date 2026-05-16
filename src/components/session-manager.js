/**
 * PASA v24.1 - Session Manager: Secure Session Injection
 * Consolidated implementation for Instagram session management
 */
export function renderSessionManager(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="insight-card p-4">
            <div class="flex items-center justify-between mb-3">
                <h3 class="text-base-700 font-semibold text-xs tracking-wider uppercase flex items-center gap-2">
                    <i data-lucide="key-round" class="w-3 h-3 text-warning-500"></i>
                    Injeção de Sessão IG
                </h3>
                <button id="refresh-session-status" 
                        class="p-1 rounded hover:bg-base-100/50 transition-colors"
                        aria-label="Atualizar status da sessão">
                    <i data-lucide="refresh-cw" class="w-4 h-4 text-base-400"></i>
                </button>
            </div>
            
            <div class="space-y-3">
                <!-- Session Status -->
                <div id="session-status" class="p-3 rounded-md text-sm flex items-center justify-between bg-base-50 border border-base-200">
                    <span class="font-medium">Status:</span>
                    <span id="session-status-text" class="px-2 py-0.5 rounded text-xs font-medium">
                        Carregando...
                    </span>
                </div>
                
                <!-- Cookie Input -->
                <div class="space-y-2">
                    <label for="ig-cookies-input" class="text-base-500 font-medium text-xs block mb-1">
                        Cookie de Sessão Instagram
                    </label>
                    <textarea id="ig-cookies-input" 
                              rows="3" 
                              class="w-full p-3 rounded-md border border-base-200 bg-base-50 text-base-700 
                                    focus:ring-2 focus:ring-warning-500 focus:border-base-100 
                                    outline-none text-sm font-mono"
                              placeholder="Cole o cookie de sessão aqui..."></textarea>
                </div>
                
                <!-- Action Button -->
                <button id="inject-cookies-btn" 
                        class="w-full p-3 rounded-md font-bold text-base-900 bg-warning-500 
                                hover:bg-warning-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
                    <i data-lucide="zap" class="w-4 h-4 mr-2"></i>
                    INJETAR E DESPAUSAR
                </button>
                
                <!-- Status Message -->
                <p id="inject-status" class="text-base-500 text-xs text-center mt-2"></p>
            </div>
        </div>
    `;

    // Initialize components
    initSessionStatus();
    initCookieInjection();
    if (window.lucide) lucide.createIcons();
}

// Initialize session status checker
async function initSessionStatus() {
    const statusEl = document.getElementById('session-status-text');
    if (!statusEl) return;
    
    try {
        const response = await fetch('/api/v1/sessions/instagram/status');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        const isActive = data.status === 'active';
        statusEl.textContent = isActive ? 'Ativa' : 'Ausente';
        statusEl.className = `px-2 py-0.5 rounded text-xs font-medium ${
            isActive ? 
            'bg-success-50 text-success-600' : 
            'bg-danger-50 text-danger-600'
        }`;
    } catch (error) {
        console.error('Failed to fetch session status:', error);
        statusEl.textContent = 'Erro';
        statusEl.className = 'px-2 py-0.5 rounded text-xs font-medium bg-danger-50 text-danger-600';
    }
}

// Initialize cookie injection form
function initCookieInjection() {
    const formEl = document.getElementById('inject-cookies-btn');
    const cookiesInput = document.getElementById('ig-cookies-input');
    const statusEl = document.getElementById('inject-status');
    
    if (!formEl || !cookiesInput || !statusEl) return;
    
    formEl.addEventListener('click', async () => {
        const cookies = cookiesInput.value.trim();
        
        if (!cookies) {
            statusEl.textContent = 'Por favor, cole o cookie de sessão primeiro.';
            statusEl.className = 'text-base-500 text-xs text-center mt-2';
            return;
        }
        
        // Disable button and show loading
        formEl.disabled = true;
        const originalContent = formEl.innerHTML;
        formEl.innerHTML = '<i data-lucide="refresh-cw" class="w-4 h-4 mr-2 animate-spin"></i> Processando...';
        if (window.lucide) lucide.createIcons();
        statusEl.textContent = 'Enviando cookie para validação...';
        statusEl.className = 'text-base-500 text-xs text-center mt-2';
        
        try {
            const response = await fetch('/api/v1/sessions/instagram/cookies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cookies })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Falha na validação do cookie');
            }
            
            statusEl.textContent = 'Cookie validado com sucesso! Reiniciando coleta...';
            statusEl.className = 'text-base-500 text-xs text-center mt-2 bg-success-50 text-success-600';
            
            // Reload after successful injection
            setTimeout(() => {
                window.location.reload();
            }, 2500);
        } catch (error) {
            console.error('Cookie injection failed:', error);
            statusEl.textContent = `Erro: ${error.message}`;
            statusEl.className = 'text-base-500 text-xs text-center mt-2 text-danger-600';
        } finally {
            // Re-enable button
            formEl.disabled = false;
            formEl.innerHTML = originalContent;
            if (window.lucide) lucide.createIcons();
        }
    });
    
    // Refresh status button
    const refreshBtn = document.getElementById('refresh-session-status');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', initSessionStatus);
    }
}
