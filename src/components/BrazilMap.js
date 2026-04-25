// SENTINELA MAP v15.1 - HIGH FIDELITY GEOGRAPHY
// Geometrias detalhadas dos estados brasileiros.

export const brazilPaths = {
    "AC": "M60.6,281.3l-5.6-7.8l23.7-17.9l21.8,9.7l13.1-18.4l22.9,6.4l6,26.5l-3.8,7.2l-21.7,18.6l-23.2-0.5l-33.3,10.2L60.6,281.3z",
    "AL": "M511.4,321.4l-7.2-7l-2.1-23.1l27-3.4l11.4,17.1l2,20.8L511.4,321.4z",
    "AM": "M156.4,24.3l37.8,20.2l31.1,41.8l-21.2,78.7l32.6,98.3l-115.1,57.9l-22.9-6.4l-13.1,18.4l-21.8-9.7l-23.7,17.9l-61.3-79.7L30.6,128.3L156.4,24.3z",
    "AP": "M411.3,47.4l19.5,6l11.4,34.7l-42.9,32.9l-23.7-18.4L411.3,47.4z",
    "BA": "M446.4,250l29.7-75.3l47.1,41.2l29,109.3l-27.5,85.4l-117,0.9L314,378.9L284.1,262L446.4,250z",
    "CE": "M522.6,197.8l57.9,22.5l1.2,59.1l-45.4-20l-13.7,1.6L522.6,197.8z",
    "DF": "M396,317h20v20h-20V317z",
    "ES": "M514,421l17.9-31.8l10.2,4.3l2.6,61.1l-17.9,6.8L514,421z",
    "GO": "M331.4,310l63.3-22.2l55.5,23.1l29.9,116.8l-69,10.1l-69.5-63L331.4,310z",
    "MA": "M395,85l84.5,48.7l36.4,137.5l-75.3,42.5l-55.5-56.5L395,85z",
    "MG": "M421,421l69-10.1l93.2,9.9l24.8,77.5l-57.2,92.9l-129.8,10.8L421,421z",
    "MS": "M206.3,327.3l125.1,22.7l69.5,63l-34.3,129.8L232.7,525L206.3,327.3z",
    "MT": "M129.3,188.7l115.1,57.9l87.1,32.3l55.5,56.5l-63.3,22.2l-125.1-22.7L129.3,188.7z",
    "PA": "M232.5,108.6l178.3-128.4l44.4,25.6l39.8,65.9l-84.5,48.7l-87.1-32.3L232.5,108.6z",
    "PB": "M580.2,220.3l31.4,17.9l0.2,24.8l-31.6,0.9L580.2,220.3z",
    "PE": "M503.2,237.4l76.8,17.1l0.9,51.2l-77.7-3.4L503.2,237.4z",
    "PI": "M409,133l51.9,10.2l61.1,126.4l-47.1-41.2L409,133z",
    "PR": "M241,434l134.1,17.8l2.6,61.1l-102.5,27L241,434z",
    "RJ": "M531,531l69.2-25.6l7.7,26.5l-59.8,25.6L531,531z",
    "RN": "M554.4,186.7l57,11.1l-31.4,40.1l-25.6-25.6L554.4,186.7z",
    "RO": "M111.4,222.9l125.4-67.7l-6,26.5l-102.5,27L111.4,222.9z",
    "RR": "M156,60.5l76.5,43.5l17.9-31.8l23.7,18.4l-76.5,48L156,60.5z",
    "RS": "M241,502l102.5-27l7.7,61.1l-110.1,25.6L241,502z",
    "SC": "M258,476.5l102.5-27l17.9,25.6L258,502L258,476.5z",
    "SE": "M588.6,357.3l22.9,34.8l-27,3.4L588.6,357.3z",
    "SP": "M394.4,434l57.2,92.9l129.8,10.8l-7.7-61.1l-119.5,42.7L394.4,434z",
    "TO": "M394.4,186.7l93.6,32.6l21.3,125.5l-75.3,42.5l-39.6-200.6L394.4,186.7z"
};

export function renderBrazilMap(containerId, stats) {
    const svg = document.getElementById(containerId);
    if (!svg) return;
    
    svg.setAttribute("viewBox", "0 0 700 700");
    
    svg.innerHTML = `
        <defs>
            <filter id="glow-intel" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="6" result="blur"/>
                <feComposite in="SourceGraphic" in2="blur" operator="over"/>
            </filter>
        </defs>
        <g id="map-root" transform="scale(0.85) translate(80, 50)">
        ${Object.entries(brazilPaths).map(([uf, d]) => {
            const info = stats[uf] || { count: 0, hate: 0 };
            let css = "state";
            if (info.count > 0) css += " has-data";
            if (info.hate > 0) css += " danger-node";
            
            const intensity = Math.min(info.count * 10, 100);
            const fill = info.count > 0 ? "rgba(59, 130, 246, " + (0.2 + (intensity/150)) + ")" : '#1e293b';
            const stroke = info.hate > 0 ? '#ef4444' : '#334155';
            
            return '<path id="state-' + uf + '" d="' + d + '" class="' + css + '" ' +
                  'fill="' + fill + '" ' +
                  'stroke="' + stroke + '" ' +
                  'style="' + (info.hate > 0 ? 'filter: url(#glow-intel); stroke-width: 1.5px;' : 'stroke-width: 0.8px;') + '" ' +
                  'onclick="window.focusState(\'' + uf + '\')">' +
                '<title>' + uf + ': ' + info.count + ' monitorados / ' + info.hate + ' alertas</title>' +
            '</path>';
        }).join('')}
        </g>
    `;
}
