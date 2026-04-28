export function renderBrazilMap(id, ufStats, onSelect) {
    const container = document.getElementById(id);
    if (!container) return;

    // Coordenadas Reais Simplificadas (Reconhecimento Geográfico Máximo)
    const mapPaths = [
        { id: 'AC', d: 'M106,448 L111,440 L131,438 L152,453 L162,476 L131,507 L95,496 L79,481 L77,460 Z', name: 'Acre' },
        { id: 'AL', d: 'M624,374 L635,372 L640,381 L630,389 L623,387 Z', name: 'Alagoas' },
        { id: 'AP', d: 'M397,143 L413,138 L440,154 L443,184 L415,193 L398,172 Z', name: 'Amapá' },
        { id: 'AM', d: 'M87,192 L223,178 L314,244 L323,347 L167,469 L132,434 L115,333 L87,290 Z', name: 'Amazonas' },
        { id: 'BA', d: 'M485,310 L549,307 L603,348 L623,439 L575,510 L486,499 L458,409 Z', name: 'Bahia' },
        { id: 'CE', d: 'M558,221 L596,219 L617,250 L599,282 L564,278 L552,253 Z', name: 'Ceará' },
        { id: 'DF', d: 'M461,445 L477,445 L477,460 L461,460 Z', name: 'Distrito Federal' },
        { id: 'ES', d: 'M590,518 L608,525 L605,558 L588,555 Z', name: 'Espírito Santo' },
        { id: 'GO', d: 'M404,383 L480,391 L490,490 L425,502 L400,453 Z', name: 'Goiás' },
        { id: 'MA', d: 'M444,198 L514,213 L547,301 L484,306 L453,234 Z', name: 'Maranhão' },
        { id: 'MT', d: 'M252,342 L394,321 L403,450 L320,497 L241,441 Z', name: 'Mato Grosso' },
        { id: 'MS', d: 'M314,506 L385,504 L404,591 L328,623 L298,582 Z', name: 'Mato Grosso do Sul' },
        { id: 'MG', d: 'M468,506 L571,514 L588,610 L485,639 L444,570 Z', name: 'Minas Gerais' },
        { id: 'PA', d: 'M316,183 L435,178 L450,230 L400,317 L315,338 Z', name: 'Pará' },
        { id: 'PB', d: 'M611,273 L637,276 L641,299 L612,298 Z', name: 'Paraíba' },
        { id: 'PR', d: 'M355,640 L442,642 L453,695 L368,707 Z', name: 'Paraná' },
        { id: 'PE', d: 'M582,286 L638,299 L635,330 L591,327 Z', name: 'Pernambuco' },
        { id: 'PI', d: 'M508,217 L553,227 L542,305 L500,306 L486,252 Z', name: 'Piauí' },
        { id: 'RJ', d: 'M546,606 L584,614 L580,638 L543,635 Z', name: 'Rio de Janeiro' },
        { id: 'RN', d: 'M604,244 L639,248 L642,271 L608,270 Z', name: 'Rio Grande do Norte' },
        { id: 'RS', d: 'M351,743 L440,750 L432,831 L338,819 Z', name: 'Rio Grande do Sul' },
        { id: 'RO', d: 'M175,465 L247,445 L252,504 L181,516 Z', name: 'Rondônia' },
        { id: 'RR', d: 'M188,83 L256,80 L273,153 L204,166 Z', name: 'Roraima' },
        { id: 'SC', d: 'M375,708 L452,709 L458,744 L382,741 Z', name: 'Santa Catarina' },
        { id: 'SP', d: 'M408,598 L482,605 L477,661 L403,663 L389,634 Z', name: 'São Paulo' },
        { id: 'SE', d: 'M616,394 L630,396 L628,413 L614,411 Z', name: 'Sergipe' },
        { id: 'TO', d: 'M403,322 L451,313 L471,387 L405,378 Z', name: 'Tocantins' }
    ];

    const maxHate = Math.max(...Object.values(ufStats).map(s => s.odio || 0), 1);

    container.innerHTML = `
        <svg viewBox="0 0 700 850" style="width:100%; height:100%;" preserveAspectRatio="xMidYMid meet">
            <g transform="translate(0, -50)">
                ${mapPaths.map(uf => {
                    const data = ufStats[uf.id] || { odio: 0, alvos: 0 };
                    const hasHate = data.odio > 0;
                    const intensity = hasHate ? (data.odio / maxHate) : 0;
                    const fill = hasHate ? `rgba(239, 68, 68, ${0.1 + intensity * 0.9})` : 'rgba(30, 41, 59, 0.4)';
                    const isSelected = window.__selectedUF === uf.id;
                    const stroke = isSelected ? '#f8fafc' : hasHate ? '#ef4444' : 'rgba(255, 255, 255, 0.1)';
                    const strokeWidth = isSelected ? '4' : '1.5';
                    
                    return `
                    <path d="${uf.d}" id="path-${uf.id}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}"
                          style="cursor:pointer; transition: all 0.3s;"
                          onclick="window.handleUFClick('${uf.id}', '${uf.name}')">
                        <title>${uf.name}: ${data.odio} alertas</title>
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
