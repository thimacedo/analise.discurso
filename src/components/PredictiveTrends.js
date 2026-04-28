export function renderPredictiveTrends(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div class="glass-card" style="padding: 24px; border-left: 4px solid #10b981;"><h4 style="font-size: 10px; color: #10b981; font-weight: 800;">TENDÊNCIA PREDITIVA</h4><p style="font-size: 14px; color: white; margin-top: 8px;">Estabilidade detectada em 85% dos alvos.</p></div>';
}