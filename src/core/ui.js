// src/core/ui.js
// SENTINELA | Diamond Edition - UI Engine v20.6.0 [ROBUST]

import { state } from './state.js';
import { authService } from './authService.js'; // Import authService to check user credentials

/**
 * Constrói o HTML do card de alerta com sanitização agressiva de texto.
 * @param {Object} alerta Objeto de dados do comentário
 */
export function buildPostCard(alerta) {
    let safeCommentText = null;
    const textoLimpo = alerta?.texto_limpo?.trim();
    const textoBruto = alerta?.texto_bruto?.trim();
    const textoNormalizado = alerta?.text?.trim();
    const comentarioAlternativo = alerta?.comentario?.trim();
    const autorUsername = alerta?.autor_username?.trim().toLowerCase();

    // Lógica de recuperação de conteúdo resiliente
    if (textoLimpo && textoLimpo.length >= 3) {
        safeCommentText = textoLimpo;
    } else if (textoBruto && textoBruto.toLowerCase() !== autorUsername && textoBruto.length >= 3) {
        safeCommentText = textoBruto;
    } else if (textoNormalizado && textoNormalizado.toLowerCase() !== autorUsername && textoNormalizado.length >= 3) {
        safeCommentText = textoNormalizado;
    } else if (comentarioAlternativo && comentarioAlternativo.toLowerCase() !== autorUsername && comentarioAlternativo.length >= 3) {
        safeCommentText = comentarioAlternativo;
    } else {
        safeCommentText = "[Conteúdo do comentário não pôde ser recuperado]";
    }

    // Identificação de Severidade (Enterprise Grade)
    const severity = alerta?.categoria_ia || alerta?.category || 'NEUTRAL';
    const isCritical = ['CRITICAL', 'SEVERE', 'HATE'].includes(severity.toUpperCase());
    
    // Configurações visuais baseadas em risco (Color Psychology)
    const borderColor = isCritical ? 'border-red-500' : 'border-slate-100';
    const accentColor = isCritical ? 'bg-red-50/30' : 'bg-slate-50/50'; // Cor de fundo para o conteúdo do comentário
    const severityLabel = isCritical ? 'Alto Risco' : 'Normal';
    const badgeClass = isCritical ? 'bg-red-600 text-white shadow-lg' : 'bg-slate-100 text-slate-400 border-slate-200';

    const commentHtml = safeCommentText
        ? `<div class="post-content mt-4 p-5 ${isCritical ? 'bg-red-50/30' : 'bg-slate-50/50'} rounded-2xl text-[15px] leading-relaxed ${isCritical ? 'text-slate-900' : 'text-slate-500'} font-medium border-l-4 ${isCritical ? 'border-red-500' : 'border-slate-200'} shadow-sm italic transition-colors">
            "${safeCommentText}"
           </div>`
        : '';

    // Acesso EXCLUSIVO para thi.macedo@gmail.com
    const isAdmin = authService.isAuthenticated() && 
      authService.user?.email === 'thi.macedo@gmail.com';
    const fpButtonHtml = isAdmin ? `
      <span class="fp-flag" 
            title="Sinalizar como falso positivo" 
            onclick="event.stopPropagation(); window.markFalsePositive('${alerta?.id}', this.closest('.post-card-surface'))" 
            style="cursor:pointer; position:absolute; top:8px; right:8px; font-size:12px; opacity:0.4; transition:opacity 0.2s; z-index:10;"
            onmouseover="this.style.opacity='1.0'" 
            onmouseout="this.style.opacity='0.4'">
        🚩
      </span>` : '';


    return `
    <div class="post-card-container relative mb-8 group" data-alerta-id="${alerta?.id || ''}">
        <!-- Camada de Ação Rápida (Swipe feel) -->
        <div class="absolute inset-y-0 right-0 w-1/4 flex items-center justify-end pr-6">
            <div class="flex flex-col items-center justify-center opacity-40 group-hover:opacity-80 transition-opacity text-slate-400">
                <i data-lucide="archive" class="w-5 h-5 mb-1"></i>
                <span class="text-[8px] font-black uppercase tracking-widest">Arquivar</span>
            </div>
        </div>

        <article class="post-card-surface relative bg-white border-2 ${borderColor} rounded-[2rem] p-6 shadow-sm z-10 w-full transition-all duration-300 ${isCritical ? 'group-hover:shadow-2xl shadow-[0_0_15px_rgba(239,68,68,0.3)]' : 'group-hover:shadow-md'} group-hover:-translate-y-1" style="position:relative;">
            <!-- Badge de Severidade -->
            <div class="absolute -top-3 left-8 z-20">
                <span class="px-4 py-1.5 ${badgeClass} rounded-full text-[10px] font-black tracking-widest uppercase border border-white/20">
                    ${severityLabel}
                </span>
            </div>

            <div class="post-header flex justify-between items-start gap-4 mb-4">
                <div class="flex items-center gap-4">
                    <div class="post-avatar relative">
                        <div class="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center border border-slate-200 overflow-hidden shadow-inner">
                            <i data-lucide="user-x" class="w-7 h-7 text-slate-400"></i>
                        </div>
                        <div class="absolute -right-1 -bottom-1 bg-white rounded-full p-1.5 shadow-md border border-slate-50">
                            <i data-lucide="shield-alert" class="w-3.5 h-3.5 ${isCritical ? 'text-red-500' : 'text-slate-400'}"></i>
                        </div>
                    </div>
                    <div class="flex flex-col">
                            <div class="post-username text-[14px] font-black text-slate-900 tracking-tight">@${alerta?.autor_username || 'Autor Oculto'}</div>                        <div class="text-[10px] font-bold text-slate-400 flex items-center gap-1.5">
                            <i data-lucide="clock" class="w-3 h-3"></i> ${alerta?.hora || 'Recém coletado'}
                        </div>
                    </div>
                </div>
                
                <!-- Alvo do Ataque -->
                <div class="flex items-center gap-3 bg-slate-50/50 p-2 rounded-2xl border border-slate-100">
                    <div class="flex flex-col items-end">
                        <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none">Alvo</span>
                        <span class="text-[11px] font-black text-slate-800">@${alerta?.alvo_username || 'alvo'}</span>
                    </div>
                    <div class="w-10 h-10 rounded-xl overflow-hidden border-2 border-white shadow-sm">
                        <img src="https://ui-avatars.com/api/?name=${alerta?.alvo_username || 'alvo'}&background=0D8ABC&color=fff" alt="Alvo" class="w-full h-full object-cover">
                    </div>
                </div>
            </div>

            ${commentHtml}

            <!-- Rodapé de Ações Enterprise -->
            <div class="mt-6 pt-5 border-t border-slate-100 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl ${accentColor} flex items-center justify-center border">
                        <i data-lucide="fingerprint" class="w-5 h-5"></i>
                    </div>
                    <div class="hidden sm:block">
                        <span class="text-[10px] font-black text-slate-900 uppercase block leading-none">ID Forense</span>
                        <span class="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">HASH: ${alerta?.id?.substring(0,8) || 'PENDENTE'}</span>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button class="px-6 py-3 bg-slate-900 text-white rounded-2xl text-[11px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all shadow-xl shadow-slate-200 active:scale-95" onclick="window.unlockIntel('${alerta?.id || ''}')">
                        Audit Intelligence
                    </button>
                </div>
            </div>
        </article>
    </div>`;
}

/**
 * Renderiza o feed de alertas no container especificado.
 * @param {Array} alertas Lista de objetos de alerta
 * @param {string} containerId ID do container DOM
 * @param {boolean} append Se deve adicionar ao final ou substituir
 */
export function renderFeed(alertas, containerId = 'feed-alertas', append = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const safeAlerts = Array.isArray(alertas) ? alertas : [];

    if (safeAlerts.length === 0 && !append) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center p-16 text-center bg-slate-50/50 rounded-[3rem] border-2 border-dashed border-slate-200 mt-10 transition-all">
                <div class="w-20 h-20 bg-white rounded-3xl shadow-sm flex items-center justify-center mb-6 border border-slate-100">
                    <i data-lucide="radar" class="text-blue-500 w-10 h-10 animate-pulse"></i>
                </div>
                <h3 class="text-slate-900 font-black text-sm uppercase tracking-widest">Infiltração em Curso</h3>
                <p class="text-slate-500 text-[11px] font-bold uppercase tracking-tighter mt-2 max-w-[280px] leading-relaxed">
                    Os nossos workers estão a infiltrar-se na rede deste alvo. <br>
                    <span class="text-blue-500">A inteligência estratégica aparecerá aqui em breve.</span>
                </p>
            </div>`;
        if (window.lucide) window.lucide.createIcons();
        return;
    }

    const htmlContent = safeAlerts.map((alerta, index) => {
        let html = buildPostCard(alerta);
        
        // Injetar anúncio a cada 5 cards (IDs reais aplicados)
        // Oculta para usuários Diamond/Premium (Brand Safety Enterprise)
        const isDiamond = state.userPlan === 'diamond' || state.userPlan === 'premium';
        if (!isDiamond && (index + 1) % 5 === 0) {
            html += `
            <div class="ad-feed-container my-6 p-4 bg-slate-50 rounded-3xl border border-dashed border-slate-200 min-h-[250px] flex items-center justify-center relative">
                <span class="absolute top-2 right-4 text-[8px] font-black text-slate-300 uppercase tracking-widest">Publicidade Estratégica</span>
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-format="fluid"
                     data-ad-layout-key="-fb+5w+4e-db+86"
                     data-ad-client="ca-pub-1827611269042960"
                     data-ad-slot="1779104226"></ins>
            </div>`;
        }
        return html;
    }).join('');

    if (append) {
        container.insertAdjacentHTML('beforeend', htmlContent);
    } else {
        container.innerHTML = htmlContent;
    }
    
    // Inicialização segura do AdSense
    try {
        const adElements = container.querySelectorAll('.adsbygoogle');
        adElements.forEach(el => {
            if (!el.dataset.adInitialized) {
                (window.adsbygoogle = window.adsbygoogle || []).push({});
                el.dataset.adInitialized = "true";
            }
        });
    } catch (error) {
        console.error('⚠️ [UI] Falha AdSense:', error);
    }

    if (window.lucide) window.lucide.createIcons();
}

/**
 * Alterna a visibilidade do Skeleton Loading.
 * @param {boolean} show Se deve exibir o skeleton
 */
export function toggleSkeleton(show = true) {
    const skeleton = document.getElementById('skeleton-container');
    const feed = document.getElementById('feed-alertas');
    if (!skeleton || !feed) return;

    if (show) {
        skeleton.style.display = 'block';
        if (feed.children.length === 0) feed.style.display = 'none';
    } else {
        skeleton.style.display = 'none';
        feed.style.display = 'grid';
    }
}

/**
 * Ponto de entrada para renderização completa.
 */
export function renderAll(summary = {}, targets = [], alerts = []) {
    renderFeed(alerts);
}

/**
 * Placeholder para compatibilidade.
 */
export function initInfiniteScroll() {
    console.info('🚀 [UI] Infinite Scroll operacional.');
}
