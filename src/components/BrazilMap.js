/**
 * BrazilMap.js - Componente Geopolítico Sentinela
 * v17.2.5 - High-Accuracy Contiguous Mapping
 */
export function renderBrazilMap(id, ufStats, onSelect) {
    const container = document.getElementById(id);
    if (!container) return;

    // Coordenadas Geográficas Alinhadas (Sistema de Grade Unificado)
    const mapPaths = [
        { id: 'AC', name: 'Acre', d: 'M57,364 L79,343 L99,353 L106,378 L87,398 L51,391 Z' },
        { id: 'AL', name: 'Alagoas', d: 'M461,304 L473,303 L477,314 L464,318 Z' },
        { id: 'AP', name: 'Amapá', d: 'M292,109 L308,103 L329,119 L323,138 L302,142 Z' },
        { id: 'AM', name: 'Amazonas', d: 'M44,204 L146,183 L208,235 L217,312 L101,374 L75,342 L66,281 Z' },
        { id: 'BA', name: 'Bahia', d: 'M358,284 L411,281 L451,324 L461,389 L422,442 L356,432 L340,361 Z' },
        { id: 'CE', name: 'Ceará', d: 'M412,192 L442,190 L457,212 L443,239 L416,236 Z' },
        { id: 'DF', name: 'Distrito Federal', d: 'M341,392 L353,392 L343,403 L341,403 Z' },
        { id: 'ES', name: 'Espírito Santo', d: 'M436,447 L450,453 L448,478 L435,475 Z' },
        { id: 'GO', name: 'Goiás', d: 'M298,342 L354,348 L361,424 L313,433 L295,394 Z' },
        { id: 'MA', name: 'Maranhão', d: 'M327,153 L379,165 L404,275 L357,280 L333,181 Z' },
        { id: 'MT', name: 'Mato Grosso', d: 'M175,258 L301,241 L305,340 L240,378 L180,334 Z' },
        { id: 'MS', name: 'Mato Grosso do Sul', d: 'M221,382 L274,381 L288,446 L230,471 L210,438 Z' },
        { id: 'MG', name: 'Minas Gerais', d: 'M344,437 L421,444 L434,518 L356,541 L326,487 Z' },
        { id: 'PA', name: 'Pará', d: 'M222,143 L320,138 L340,178 L302,243 L238,259 Z' },
        { id: 'PB', name: 'Paraíba', d: 'M452,229 L471,232 L474,249 L453,248 Z' },
        { id: 'PR', name: 'Paraná', d: 'M252,484 L317,485 L325,526 L262,535 Z' },
        { id: 'PE', name: 'Pernambuco', d: 'M430,240 L472,249 L470,274 L437,271 Z' },
        { id: 'PI', name: 'Piauí', d: 'M375,168 L409,176 L400,277 L370,278 Z' },
        { id: 'RJ', name: 'Rio de Janeiro', d: 'M403,516 L432,523 L429,541 L401,539 Z' },
        { id: 'RN', name: 'Rio Grande do Norte', d: 'M447,208 L474,211 L476,227 L450,226 Z' },
        { id: 'RS', name: 'Rio Grande do Sul', d: 'M250,563 L317,568 L311,631 L240,622 Z' },
        { id: 'RO', name: 'Rondônia', d: 'M117,351 L171,335 L180,381 L127,392 Z' },
        { id: 'RR', name: 'Roraima', d: 'M126,58 L177,56 L190,113 L138,123 Z' },
        { id: 'SC', name: 'Santa Catarina', d: 'M267,536 L325,537 L330,564 L273,562 Z' },
        { id: 'SP', name: 'São Paulo', d: 'M292,453 L347,458 L343,501 L288,502 L278,480 Z' },
        { id: 'SE', name: 'Sergipe', d: 'M454,289 L465,290 L463,303 L452,302 Z' },
        { id: 'TO', name: 'Tocantins', d: 'M297,243 L340,240 L354,342 L298,336 Z' }
    ];

    const maxHate = Math.max(...Object.values(ufStats).map(s => s.odio || 0), 1);

    container.innerHTML = `
        <svg viewBox="0 0 550 700" class="sentinela-map-svg">
            <defs>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <g transform="translate(20, 20)">
                ${mapPaths.map(uf => {
                    const data = ufStats[uf.id] || { odio: 0, alvos: 0 };
                    const hasHate = data.odio > 0;
                    const intensity = hasHate ? (data.odio / maxHate) : 0;
                    const fill = hasHate ? `rgba(239, 68, 68, ${0.15 + intensity * 0.85})` : 'rgba(148, 163, 184, 0.08)';
                    const isSelected = window.__selectedUF === uf.id;
                    const stroke = isSelected ? '#38bdf8' : (hasHate ? '#ef4444' : 'rgba(255, 255, 255, 0.1)');
                    const strokeWidth = isSelected ? '3' : '1';
                    const pulseClass = (intensity > 0.75) ? 'map-pulse' : '';

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
