// src/core/ui.js

export function buildPostCard(alerta) {
    let safeCommentText = null;
    const textoLimpo = alerta?.texto_limpo?.trim();
    const textoBruto = alerta?.texto_bruto?.trim();
    const textoNormalizado = alerta?.text?.trim();
    const comentarioAlternativo = alerta?.comentario?.trim();
    const autorUsername = alerta?.autor_username?.trim().toLowerCase();

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

    const commentHtml = safeCommentText
        ? `<div class="post-content mt-4 p-5 bg-slate-50 rounded-2xl text-[15px] leading-relaxed text-slate-800 font-medium border-l-8 border-blue-500 shadow-inner italic">
            "${safeCommentText}"
           </div>`
        : '';

    return `
    <div class="post-card-container relative mb-6 rounded-3xl overflow-hidden bg-slate-900" data-alerta-id="${alerta?.id || ''}">
        <div class="absolute inset-y-0 right-0 w-1/3 flex items-center justify-end pr-8">
            <div class="flex flex-col items-center justify-center opacity-60 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-6 h-6 mb-1"><rect width="20" height="5" x="2" y="3" rx="1"></rect><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"></path><path d="M10 12h4"></path></svg>
                <span class="text-[10px] font-black uppercase tracking-widest">Arquivar</span>
            </div>
        </div>
        <article class="post-card-surface animate-in is-locked relative bg-white border border-slate-200 rounded-3xl p-6 shadow-sm z-10 w-full h-full transition-all hover:shadow-xl hover:-translate-y-1">
            <div class="absolute top-4 left-6 z-20">
                <span class="px-3 py-1 bg-slate-900 text-white rounded-full text-[9px] font-black tracking-widest shadow-sm uppercase border border-slate-800">Suspeito</span>
            </div>
            <div class="post-header flex justify-between items-center gap-4 mb-6">
                <div class="flex items-center gap-4 mt-2">
                    <div class="post-avatar relative">
                        <img src="https://ui-avatars.com/api/?name=?&background=334155&color=fff" alt="Suspeito" class="w-12 h-12 rounded-2xl blur-[4px] select-none pointer-events-none object-cover border border-slate-100 shadow-sm" loading="lazy">
                        <div class="absolute -right-2 -bottom-2 bg-white rounded-full p-1.5 shadow-md border border-slate-50">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-3 h-3 text-slate-500"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                        </div>
                    </div>
                    <div class="flex flex-col">
                        <div class="post-username text-[13px] font-black text-slate-900 blur-[6px] select-none pointer-events-none opacity-50">agressor_protegido</div>
                        <div class="text-[10px] font-bold text-slate-400 flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-2.5 h-2.5"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg> ${alerta?.hora || '00:00:00'}
                        </div>
                    </div>
                </div>
                <div class="flex items-center gap-4 text-right">
                    <div class="flex flex-col items-end min-w-0 max-w-[120px]">
                        <div class="px-2 py-1 bg-blue-50 text-blue-800 rounded-lg text-[10px] font-black uppercase tracking-tighter truncate w-full">@${alerta?.alvo_username || 'alvo'}</div>
                        <div class="text-[9px] font-black text-slate-700 uppercase truncate w-full mt-1">${alerta?.alvo_nome || 'Alvo'}</div>
                    </div>
                    <div class="w-12 h-12 rounded-2xl overflow-hidden border-2 border-slate-50 shadow-sm transition-transform group-hover:scale-110">
                        <img src="https://ui-avatars.com/api/?name=${alerta?.alvo_username || 'alvo'}&background=0D8ABC&color=fff" alt="Alvo" class="w-full h-full object-cover">
                    </div>
                </div>
            </div>
            ${commentHtml}
            <div class="mt-6 pt-5 border-t border-slate-100 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center border border-amber-100">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 text-amber-500"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                    </div>
                    <div>
                        <span class="text-[10px] font-black text-slate-900 uppercase block leading-none">Dados Ocultos</span>
                        <span class="text-[8px] font-bold text-slate-400 uppercase tracking-tighter">Upgrade STN necessário</span>
                    </div>
                </div>
                <button class="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 transition-all shadow-xl shadow-slate-200" onclick="window.unlockIntel('${alerta?.id || ''}')">Revelar Dados</button>
            </div>
        </article>
    </div>`;
}

export function renderFeed(alertas, containerId = 'feed-alertas', append = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!Array.isArray(alertas) || alertas.length === 0) {
        if (!append) container.innerHTML = `<div class="flex flex-col items-center justify-center p-12 text-center bg-slate-50 rounded-3xl border border-dashed border-slate-200 mt-10"><div class="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mb-4"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate-300 w-8 h-8"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg></div><h3 class="text-slate-900 font-black text-sm uppercase tracking-widest">Silêncio no Horizonte</h3><p class="text-slate-500 text-[10px] font-bold uppercase tracking-tighter mt-1 max-w-[200px]">Nenhum alerta detectado.</p></div>`;
        return;
    }

    const htmlContent = alertas.map((alerta, index) => {
        let html = buildPostCard(alerta);
        if ((index + 1) % 5 === 0) html += `<div class="ad-feed-container my-6 p-4 bg-slate-50 rounded-3xl border border-dashed border-slate-200 min-h-[250px] flex items-center justify-center"><ins class="adsbygoogle" style="display:block" data-ad-format="fluid" data-ad-layout-key="-fb+5w+4e-db+86" data-ad-client="ca-pub-1827611269042960" data-ad-slot="XXXXXX"></ins><script>(window.adsbygoogle = window.adsbygoogle || []).push({});</script></div>`;
        return html;
    }).join('');

    if (append) container.insertAdjacentHTML('beforeend', htmlContent);
    else container.innerHTML = htmlContent;
    
    if (window.lucide) window.lucide.createIcons();
}

export function initSwipeGestures() {
    console.log('Swipe Gestures Initialized');
}

export function renderAll(summary = {}, targets = [], alerts = []) {
    renderFeed(alerts || []);
    if (window.lucide) window.lucide.createIcons();
}
