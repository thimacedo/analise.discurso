// SENTINELA TECH-MAP v1.0 (Stylized Low-Poly / Hex-Style)
// Versão focada em impacto visual e sinalização de War-Room

export const techStates = {
    "AC": "M50 350 L70 340 L80 360 L60 370 Z",
    "AM": "M50 200 L120 180 L180 220 L150 300 L60 340 Z",
    "RR": "M130 170 L170 150 L190 180 L150 200 Z",
    "PA": "M190 190 L280 140 L330 200 L280 280 L190 230 Z",
    "AP": "M290 130 L320 120 L330 150 L300 160 Z",
    "MA": "M340 190 L390 210 L380 280 L330 260 Z",
    "PI": "M400 220 L440 240 L430 310 L390 290 Z",
    "CE": "M450 220 L490 230 L480 270 L440 250 Z",
    "RN": "M490 240 L520 250 L510 280 L480 270 Z",
    "PB": "M490 280 L520 290 L510 320 L480 310 Z",
    "PE": "M440 310 L510 330 L500 360 L430 340 Z",
    "AL": "M480 360 L505 370 L500 390 L475 380 Z",
    "SE": "M470 390 L490 400 L485 420 L465 410 Z",
    "BA": "M350 290 L430 330 L450 430 L380 460 L340 400 Z",
    "TO": "M290 290 L330 270 L340 390 L300 410 Z",
    "MT": "M160 310 L280 300 L290 400 L180 430 Z",
    "RO": "M140 310 L170 420 L130 430 L100 330 Z",
    "GO": "M290 420 L340 410 L360 480 L310 500 Z",
    "DF": "M320 445 L335 445 L335 460 L320 460 Z",
    "MG": "M350 470 L430 440 L460 520 L380 560 L340 530 Z",
    "ES": "M470 490 L495 500 L490 530 L465 520 Z",
    "RJ": "M410 570 L450 560 L460 580 L420 590 Z",
    "SP": "M310 540 L370 570 L360 620 L300 590 Z",
    "PR": "M230 540 L290 580 L280 630 L220 590 Z",
    "SC": "M230 640 L280 640 L270 680 L220 680 Z",
    "RS": "M210 690 L280 690 L260 760 L190 740 Z",
    "MS": "M190 440 L280 410 L300 530 L210 530 Z"
};

export function renderTechMap(containerId, stats) {
    const svg = document.getElementById(containerId);
    if (!svg) return;
    
    // Ajuste de ViewBox para a versão Tech (mais vertical/espaçada)
    svg.setAttribute("viewBox", "0 0 600 800");
    
    svg.innerHTML = `
        <defs>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        ${Object.entries(techStates).map(([uf, d]) => {
            const info = stats[uf] || { ints: 0, hate: 0 };
            let css = "state";
            if (info.ints > 0) css += " has-data";
            if (info.hate > 0) css += " danger-node";
            
            return `
            <path id="state-${uf}" d="${d}" class="${css}" 
                  style="${info.hate > 0 ? 'filter: url(#glow); opacity: 1;' : 'opacity: 0.7;'}"
                  onclick="window.focusState('${uf}')">
                <title>${uf}: ${info.ints} ints / ${info.hate} alertas</title>
            </path>`;
        }).join('')}
    `;
}
