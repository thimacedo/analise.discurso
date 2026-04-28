/**
 * BrazilMap.js - Componente Geopolítico Sentinela
 * v17.1.0 - SVG High Definition & Heatmap Dynamics
 */
export function renderBrazilMap(id, ufStats, onSelect) {
    const container = document.getElementById(id);
    if (!container) return;

    const mapPaths = [
        { id: 'AC', name: 'Acre', d: 'M106,448 L111,440 L131,438 L152,453 L162,476 L131,507 L95,496 L79,481 L77,460 Z' },
        { id: 'AL', name: 'Alagoas', d: 'M624,374 L635,372 L640,381 L630,389 L623,387 Z' },
        { id: 'AP', name: 'Amapá', d: 'M397,143 L413,138 L440,154 L443,184 L415,193 L398,172 Z' },
        { id: 'AM', name: 'Amazonas', d: 'M87,192 L223,178 L314,244 L323,347 L167,469 L132,434 L115,333 L87,290 Z' },
        { id: 'BA', name: 'Bahia', d: 'M485,310 L549,307 L603,348 L623,439 L575,510 L486,499 L458,409 Z' },
        { id: 'CE', name: 'Ceará', d: 'M558,221 L596,219 L617,250 L599,282 L564,278 L552,253 Z' },
        { id: 'DF', name: 'Distrito Federal', d: 'M461,445 L477,445 L477,460 L461,460 Z' },
        { id: 'ES', name: 'Espírito Santo', d: 'M590,518 L608,525 L605,558 L588,555 Z' },
        { id: 'GO', name: 'Goiás', d: 'M404,383 L480,391 L490,490 L425,502 L400,453 Z' },
        { id: 'MA', name: 'Maranhão', d: 'M444,198 L514,213 L547,301 L484,306 L453,234 Z' },
        { id: 'MT', name: 'Mato Grosso', d: 'M252,342 L394,321 L403,450 L320,497 L241,441 Z' },
        { id: 'MS', name: 'Mato Grosso do Sul', d: 'M314,506 L385,504 L404,591 L328,623 L298,582 Z' },
        { id: 'MG', name: 'Minas Gerais', d: 'M468,506 L571,514 L588,610 L485,639 L444,570 Z' },
        { id: 'PA', name: 'Pará', d: 'M316,183 L435,178 L450,230 L400,317 L315,338 Z' },
        { id: 'PB', name: 'Paraíba', d: 'M611,273 L637,276 L641,299 L612,298 Z' },
        { id: 'PR', name: 'Paraná', d: 'M355,640 L442,642 L453,695 L368,707 Z' },
        { id: 'PE', name: 'Pernambuco', d: 'M582,286 L638,299 L635,330 L591,327 Z' },
        { id: 'PI', name: 'Piauí', d: 'M508,217 L553,227 L542,305 L500,306 L486,252 Z' },
        { id: 'RJ', name: 'Rio de Janeiro', d: 'M546,606 L584,614 L580,638 L543,635 Z' },
        { id: 'RN', name: 'Rio Grande do Norte', d: 'M604,244 L639,248 L642,271 L608,270 Z' },
        { id: 'RS', name: 'Rio Grande do Sul', d: 'M351,743 L440,750 L432,831 L338,819 Z' },
        { id: 'RO', name: 'Rondônia', d: 'M175,465 L247,445 L252,504 L181,516 Z' },
        { id: 'RR', name: 'Roraima', d: 'M188,83 L256,80 L273,153 L204,166 Z' },
        { id: 'SC', name: 'Santa Catarina', d: 'M375,708 L452,709 L458,744 L382,741 Z' },
        { id: 'SP', name: 'São Paulo', d: 'M408,598 L482,605 L477,661 L403,663 L389,634 Z' },
        { id: 'SE', name: 'Sergipe', d: 'M616,394 L630,396 L628,413 L614,411 Z' },
        { id: 'TO', name: 'Tocantins', d: 'M403,322 L451,313 L471,387 L405,378 Z' }
    ];

    const maxHate = Math.max(...Object.values(ufStats).map(s => s.odio || 0), 1);

    container.innerHTML = `
        <svg viewBox="0 0 700 850" class="sentinela-map-svg">
            <defs>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <g transform="translate(0, -20)">
                ${mapPaths.map(uf => {
                    const data = ufStats[uf.id] || { odio: 0, alvos: 0 };
                    const hasHate = data.odio > 0;
                    const intensity = hasHate ? (data.odio / maxHate) : 0;
                    const fill = hasHate ? `rgba(239, 68, 68, ${0.1 + intensity * 0.9})` : 'rgba(30, 41, 59, 0.4)';
                    const isSelected = window.__selectedUF === uf.id;
                    const stroke = isSelected ? '#38bdf8' : (hasHate ? '#ef4444' : 'rgba(255, 255, 255, 0.1)');
                    const strokeWidth = isSelected ? '4' : '1';
                    const pulseClass = (intensity > 0.7) ? 'map-pulse' : '';

                    return `
                    <path d="${uf.d}" 
                          id="uf-${uf.id}" 
                          fill="${fill}" 
                          stroke="${stroke}" 
                          stroke-width="${strokeWidth}"
                          class="uf-path ${pulseClass}"
                          filter="${isSelected ? 'url(#glow)' : ''}"
                          onclick="window.handleUFClick('${uf.id}', '${uf.name}')">
                        <title>${uf.name}: ${data.odio} alertas (${data.alvos} alvos)</title>
                    </path>`;
                }).join('')}
            </g>
        </svg>
    `;

    window.handleUFClick = (id, name) => {
        const data = ufStats[id] || { alvos: 0, odio: 0 };
        window.__selectedUF = id;
        if (typeof onSelect === 'function') onSelect(name, data, id);
    };
}
