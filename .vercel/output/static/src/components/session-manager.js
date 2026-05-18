/**
 * PASA v47.4 - Session Manager: Secure Session Injection
 * FIX: Guard against multiple instantiations on every renderApplication() call.
 *      The component is stamped once; subsequent calls are no-ops.
 */

let _initialized = false;

export function renderSessionManager(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // ── Guard: only render once ──────────────────────────────────────────────
    if (_initialized && container.dataset.smReady === '1') return;

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
                <div id="session-status"
                     class="p-3 rounded-md text-sm flex items-center justify-between bg-base-50 border border-base-200">
                    <span class="font-medium">Status:</span>
                    <span id="session-status-text"
                          class="px-2 py-0.5 rounded text-xs font-medium">
                        Carregando...
                    </span>
                </div>

                <!-- Cookie Input -->
                <div class="space-y-2">
                    <label for="ig-cookies-input"
                           class="text-base-500 font-medium text-xs block mb-1">
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
                               hover:bg-warning-600 transition-colors disabled:opacity-50
                               disabled:cursor-not-allowed flex items-center justify-center">
                    <i data-lucide="zap" class="w-4 h-4 mr-2"></i>
                    INJETAR E DESPAUSAR
                </button>

                <!-- Status Message -->
                <p id="inject-status" class="text-base-500 text-xs text-center mt-2"></p>
            </div>
        </div>
    `;

    container.dataset.smReady = '1';
    _initialized = true;

    // Wire up sub-components ONCE
    _initSessionStatus();
    _initCookieInjection();

    if (window.lucide) lucide.createIcons();
}

// ── Private helpers ──────────────────────────────────────────────────────────

async function _fetchStatus() {
    const statusEl = document.getElementById('session-status-text');
    if (!statusEl) return;

    try {
        const response = await fetch('/api/v1/sessions/instagram/status');

        // Treat non-2xx (including 500) as "unavailable" instead of throwing
        if (!response.ok) {
            _setStatusUI(statusEl, 'unavailable');
            return;
        }

        const data = await response.json();
        _setStatusUI(statusEl, data.status === 'active' ? 'active' : 'inactive');
    } catch (_err) {
        // Network error / server down — fail silently
        _setStatusUI(statusEl, 'unavailable');
    }
}

function _setStatusUI(el, status) {
    const map = {
        active:      { text: 'Ativa',        cls: 'bg-success-50 text-success-600' },
        inactive:    { text: 'Ausente',       cls: 'bg-danger-50 text-danger-600'   },
        unavailable: { text: 'Indisponível',  cls: 'bg-base-100 text-base-500'      },
    };
    const { text, cls } = map[status] || map.unavailable;
    el.textContent = text;
    el.className   = `px-2 py-0.5 rounded text-xs font-medium ${cls}`;
}

function _initSessionStatus() {
    // Fetch once on mount
    _fetchStatus();

    // Wire up manual refresh button
    const refreshBtn = document.getElementById('refresh-session-status');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', _fetchStatus, { once: false });
    }
}

function _initCookieInjection() {
    const btn       = document.getElementById('inject-cookies-btn');
    const textarea  = document.getElementById('ig-cookies-input');
    const statusEl  = document.getElementById('inject-status');

    if (!btn || !textarea || !statusEl) return;

    btn.addEventListener('click', async () => {
        const cookies = textarea.value.trim();

        if (!cookies) {
            statusEl.textContent = 'Por favor, cole o cookie de sessão primeiro.';
            return;
        }

        // Disable + spinner
        btn.disabled = true;
        const original = btn.innerHTML;
        btn.innerHTML  = '<i data-lucide="refresh-cw" class="w-4 h-4 mr-2 animate-spin"></i> Processando...';
        if (window.lucide) lucide.createIcons();

        statusEl.textContent  = 'Enviando cookie para validação...';
        statusEl.className    = 'text-base-500 text-xs text-center mt-2';

        try {
            const res = await fetch('/api/v1/sessions/instagram/cookies', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ cookies }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }

            statusEl.textContent = 'Cookie validado! Reiniciando coleta…';
            statusEl.className   = 'text-xs text-center mt-2 text-success-600';
            setTimeout(() => location.reload(), 2500);

        } catch (error) {
            statusEl.textContent = `Erro: ${error.message}`;
            statusEl.className   = 'text-xs text-center mt-2 text-danger-600';
        } finally {
            btn.disabled  = false;
            btn.innerHTML = original;
            if (window.lucide) lucide.createIcons();
        }
    });
}