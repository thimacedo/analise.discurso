// SENTINELA MAP v16.0 - STANDARD GEOGRAPHIC MODEL
// Modelo comum e reconhecível do mapa do Brasil para o Dashboard.

export const brazilPaths = {
    "AC": "M57.6,220.8l-1.3-4.5l3.2-1.7l1.5-4l4.2-1l5.5,2.6l1.3,7.2l-2.4,5.1l-10.2,0.8L57.6,220.8z",
    "AL": "M444.6,221.7l-4.2-3.1l-0.9-10.2l12-1.5l5.1,7.6l0.9,9.2L444.6,221.7z",
    "AM": "M111.3,95.2l20.4,11.3l16.8,23.2l-11.4,43.7l17.6,54.6l-62.2,32.2l-12.4-3.5l-7.1,10.2l-11.8-5.4l-12.8,9.9L31,227.1L43.8,153L111.3,95.2z",
    "AP": "M266.3,109.4l10.5,3.3l6.2,18.8l-23.2,17.9l-12.8-10L266.3,109.4z",
    "BA": "M313.2,212.7l30.8-30.7l25.6,22.4l15.7,59.4l-14.9,46.4l-63.6,0.5L254.4,282.7L238.1,219.2L313.2,212.7z",
    "CE": "M354.5,189.4l31.5,12.2l0.6,32.1l-24.7-10.9l-7.4,0.9L354.5,189.4z",
    "DF": "M285.8,254.2h10.9v10.9h-10.9V254.2z",
    "ES": "M368.1,327.9l9.7-17.3l5.5,2.3l1.4,33.2l-9.7,3.7L368.1,327.9z",
    "GO": "M250.7,267.3l34.4-12.1l30.1,12.5l16.2,63.5l-37.5,5.5l-37.8-34.2L250.7,267.3z",
    "MA": "M285.3,145.1l45.9,26.5l19.8,74.7l-40.9,23.1l-30.1-30.7L285.3,145.1z",
    "MG": "M299.3,327.9l37.5-5.5l50.6,5.4l13.5,42.1l-31.1,50.5l-70.5,5.9L299.3,327.9z",
    "MS": "M182.7,276.7l68,12.3l37.8,34.2l-18.6,70.5l-43.5,36.9L182.7,276.7z",
    "MT": "M140.9,201.3l62.5,31.5l47.3,17.5l30.1,30.7l-34.4,12.1l-68-12.3L140.9,201.3z",
    "PA": "M196.9,157.8L293.8,88l24.1,13.9l21.6,35.8l-45.9,26.5l-47.3-17.5L196.9,157.8z",
    "PB": "M385.8,201.6l17,9.7l0.1,13.5l-17.2,0.5L385.8,201.6z",
    "PE": "M344,210.9l41.7,9.3l0.5,27.8l-42.2-1.8L344,210.9z",
    "PI": "M292.9,171.1l28.2,5.5l33.2,68.7l-25.6-22.4L292.9,171.1z",
    "PR": "M201.5,335l72.9,9.7l1.4,33.2l-55.7,14.7L201.5,335z",
    "RJ": "M359,387.8l37.6-13.9l4.2,14.4l-32.5,13.9L359,387.8z",
    "RN": "M371.8,183.4l30.9,6l-17.1,21.8l-13.9-13.9L371.8,183.4z",
    "RO": "M131.2,219.9l68.1-36.8l-3.3,14.4l-55.7,14.7L131.2,219.9z",
    "RR": "M155.5,131.6l41.5,23.6l9.7-17.3l12.9,10l-41.5,26.1L155.5,131.6z",
    "RS": "M201.5,372l55.7-14.7l4.2,33.2l-59.8,13.9L201.5,372z",
    "SC": "M210.7,358.1l55.7-14.7l9.7,13.9l-55.7,14.7L210.7,358.1z",
    "SE": "M390.4,241.2l12.4,18.9l-14.7,1.8L390.4,241.2z",
    "SP": "M284.7,335l31.1,50.5l70.5,5.9l-4.2-33.2l-64.9,23.2L284.7,335z",
    "TO": "M284.7,201.6l50.8,17.7l11.6,68.2l-40.9,23.1l-21.5-109L284.7,201.6z"
};

export function renderBrazilMap(containerId, stats) {
    const svg = document.getElementById(containerId);
    if (!svg) return;
    
    // ViewBox padrão para mapa comum
    svg.setAttribute("viewBox", "0 0 500 500");
    
    svg.innerHTML = `
        <defs>
            <filter id="glow-intel" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feComposite in="SourceGraphic" in2="blur" operator="over"/>
            </filter>
        </defs>
        <g id="map-root">
        ${Object.entries(brazilPaths).map(([uf, d]) => {
            const info = stats[uf] || { count: 0, hate: 0 };
            let css = "state";
            if (info.count > 0) css += " has-data";
            if (info.hate > 0) css += " danger-node";
            
            const intensity = Math.min(info.count * 10, 100);
            const fill = info.count > 0 ? "rgba(59, 130, 246, " + (0.3 + (intensity/200)) + ")" : '#1e293b';
            const stroke = info.hate > 0 ? '#ef4444' : '#334155';
            
            return '<path id="state-' + uf + '" d="' + d + '" class="' + css + '" ' +
                  'fill="' + fill + '" ' +
                  'stroke="' + stroke + '" ' +
                  'style="' + (info.hate > 0 ? 'filter: url(#glow-intel); stroke-width: 1.2px;' : 'stroke-width: 0.5px;') + '" ' +
                  'onclick="window.focusState(\'' + uf + '\')">' +
                '<title>' + uf + ': ' + info.count + ' monitorados / ' + info.hate + ' alertas</title>' +
            '</path>';
        }).join('')}
        </g>
    `;
}
