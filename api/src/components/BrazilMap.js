// SENTINELA SQUARE-GRID v2.1 - ERROR RESILIENT CARTOGRAM
// Modelo de grade quadrada com proteção contra dados nulos.

const boxSize = 50; 
const gap = 4; 

const gridLayout = {
    "BR": { r: 0, c: 0 },
    "RR": { r: 0, c: 2 }, "AP": { r: 0, c: 4 },
    "AM": { r: 1, c: 1 }, "PA": { r: 1, c: 2 }, "MA": { r: 1, c: 3 }, "PI": { r: 1, c: 4 }, "CE": { r: 1, c: 5 }, "RN": { r: 1, c: 6 },
    "AC": { r: 2, c: 0 }, "RO": { r: 2, c: 1 }, "MT": { r: 2, c: 2 }, "TO": { r: 2, c: 3 }, "BA": { r: 2, c: 4 }, "PE": { r: 2, c: 5 }, "PB": { r: 2, c: 6 },
    "MS": { r: 3, c: 1 }, "GO": { r: 3, c: 2 }, "DF": { r: 3, c: 3 }, "MG": { r: 3, c: 4 }, "AL": { r: 3, c: 5 }, "SE": { r: 3, c: 6 },
    "PR": { r: 4, c: 2 }, "SP": { r: 4, c: 3 }, "RJ": { r: 4, c: 4 }, "ES": { r: 4, c: 5 },
    "RS": { r: 5, c: 1 }, "SC": { r: 5, c: 2 }
};

export function renderBrazilMap(containerId, stats = {}) {
    const svg = document.getElementById(containerId);
    if (!svg) return;
    
    // Proteção: Garantir que stats é um objeto válido
    const safeStats = stats || {};
    
    svg.setAttribute("viewBox", "0 0 550 450");
    
    svg.innerHTML = `
        <defs>
            <filter id="glow-square" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="5" result="blur"/>
                <feComposite in="SourceGraphic" in2="blur" operator="over"/>
            </filter>
        </defs>
        <g id="grid-root" transform="translate(40, 40)">
        ${Object.entries(gridLayout).map(([uf, pos]) => {
            const info = safeStats[uf] || { count: 0, hate: 0 };
            const x = pos.c * (boxSize + gap);
            const y = pos.r * (boxSize + gap);
            
            const isBR = uf === "BR";
            const hasHate = info.hate > 0;
            
            let fill = info.count > 0 ? (hasHate ? 'rgba(239, 68, 68, 0.5)' : 'rgba(59, 130, 246, 0.4)') : 'rgba(30, 41, 59, 0.6)';
            if(isBR) fill = 'rgba(59, 130, 246, 0.2)';
            
            const stroke = hasHate ? '#ef4444' : (info.count > 0 ? '#3b82f6' : 'rgba(255, 255, 255, 0.05)');
            
            return `
            <g class="state-group cursor-pointer transition-all duration-300 hover:opacity-80" onclick="window.focusState('${uf}')">
                <rect id="state-${uf}" x="${x}" y="${y}" width="${boxSize}" height="${boxSize}" 
                      rx="${isBR ? '25' : '12'}"
                      fill="${fill}" 
                      stroke="${stroke}" 
                      stroke-width="${isBR ? '2' : (hasHate ? '3' : '1')}"
                      class="state-rect"
                      style="${hasHate ? 'filter: url(#glow-square);' : ''}">
                </rect>
                <text x="${x + boxSize/2}" y="${y + boxSize/2}" 
                      text-anchor="middle" 
                      alignment-baseline="middle" 
                      fill="${isBR || info.count > 0 ? '#fff' : '#475569'}" 
                      class="${isBR ? 'text-[14px]' : 'text-xs'} font-black pointer-events-none tracking-tighter">
                    ${uf}
                </text>
            </g>`;
        }).join('')}
        </g>
    `;
}
