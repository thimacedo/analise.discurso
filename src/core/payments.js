// SENTINELA | Diamond Edition - Payment Module
// Gerencia redirecionamentos de pagamento e instruções de checkout

const PAYPAL_EMAIL = 'thi.macedo@gmail.com';
const CURRENCY = 'BRL';
const PRECO_PLANO = 49.90;

export async function initiatePayment(method) {
    const modalContent = document.querySelector('#upgrade-modal .modal-content');
    if (!modalContent) return;

    const userEmail = prompt("Para identificar seu pagamento, digite seu e-mail de cadastro:");
    
    if (!userEmail || !userEmail.includes('@')) {
        alert('E-mail inválido para identificação.');
        return;
    }

    if (method === 'pix') {
        alert("Pagamento via PIX indisponível no momento. Por favor, utilize o PayPal.");
        return;
    } 
    else if (method === 'paypal') {
        // Redireciona para o PayPal com valor e descrição identificada pelo e-mail do usuário
        const paypalUrl = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=${encodeURIComponent(PAYPAL_EMAIL)}&item_name=Sentinela Pro - ${userEmail}&amount=${PRECO_PLANO}&currency_code=${CURRENCY}&no_shipping=1`;
        
        window.open(paypalUrl, '_blank');
        renderPaypalInstructions(modalContent, userEmail);
    }
}

function renderPaypalInstructions(container, email) {
    container.innerHTML = `
        <div style="text-align: center; padding: 10px;">
            <div style="width:56px;height:56px;border-radius:14px;background:rgba(37,99,235,0.1);display:flex;align-items:center;justify-content:center;margin:0 auto 20px">
                <i data-lucide="external-link" style="width:24px;height:24px;color:#60a5fa"></i>
            </div>
            <h2 style="color:white; font-size: 20px; margin-bottom: 10px; font-family:'Space Grotesk', sans-serif;">Redirecionado ao PayPal</h2>
            
            <div style="background: rgba(37, 99, 235, 0.1); padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(37, 99, 235, 0.2);">
                <p style="color: #60a5fa; font-size: 14px; font-weight: bold; margin-bottom: 5px;">🅿️ Janela de Checkout Aberta</p>
                <p style="color: rgba(255,255,255,0.8); font-size: 13px;">
                    O valor foi travado em <strong style="color:white;">R$ ${PRECO_PLANO.toFixed(2)}</strong>.<br>
                    Se a janela não abriu, permita pop-ups.
                </p>
            </div>

            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px dashed rgba(255,255,255,0.2); margin-bottom: 20px;">
                <p style="color: #fbbf24; font-size: 11px; font-weight: 800; margin-bottom: 8px; text-transform: uppercase;">⚠️ PASSO FINAL OBRIGATÓRIO</p>
                <p style="color: rgba(255,255,255,0.7); font-size: 12px; line-height: 1.4;">
                    Após concluir o pagamento, envie o print do comprovante para:<br>
                    <strong style="color:white;">thi.macedo@gmail.com</strong><br>
                    <span style="font-size: 11px; opacity: 0.6;">Identificador: Pagamento Sentinela - ${email}</span>
                </p>
            </div>

            <button onclick="location.reload()" style="background: transparent; border: none; color: rgba(255,255,255,0.5); cursor: pointer; font-size: 13px; text-decoration: underline;">
                Voltar ao Painel
            </button>
        </div>
    `;
    if (window.lucide) lucide.createIcons();
}

// Exposição global para chamadas via HTML onclick
window.initiatePayment = initiatePayment;
