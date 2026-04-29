// /src/core/payments.js

const PAYPAL_EMAIL = 'thi.macedo@gmail.com';
const CURRENCY = 'BRL';
const PRECO_PLANO = 279.90; // Valor atualizado para R$ 279,90

export async function initiatePayment(method) {
    const modalContent = document.querySelector('.modal-content');
    const userEmail = prompt("Para identificar seu pagamento, digite seu e-mail de cadastro:");
    
    if (!userEmail || !userEmail.includes('@')) {
        alert('E-mail inválido.');
        return;
    }

    // PIX DESATIVADO TEMPORARIAMENTE
    if (method === 'pix') {
        alert("Pagamento via PIX indisponível no momento. Use o PayPal.");
        return;
    } 
    else if (method === 'paypal') {
        // Redireciona direto para o PayPal com o novo valor travado
        const paypalUrl = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=${encodeURIComponent(PAYPAL_EMAIL)}&item_name=Sentinela Pro - ${userEmail}&amount=${PRECO_PLANO}&currency_code=${CURRENCY}&no_shipping=1`;
        
        window.open(paypalUrl, '_blank');
        renderPaypalInstructions(modalContent, userEmail);
    }
}

function renderPaypalInstructions(container, email) {
    container.innerHTML = `
        <div style="text-align: center; padding: 10px;">
            <h2 style="color:white; font-size: 20px; margin-bottom: 10px;">Redirecionado ao PayPal</h2>
            
            <div style="background: rgba(37, 99, 235, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                <p style="color: #60a5fa; font-size: 16px; font-weight: bold; margin-bottom: 10px;">🅿️ Janela do PayPal Aberta</p>
                <p style="color: rgba(255,255,255,0.8); font-size: 14px;">
                    Se a janela não abriu, permita pop-ups no seu navegador.<br>
                    O valor foi travado em <strong style="color:white;">$ ${PRECO_PLANO.toFixed(2)} BRL</strong>.
                </p>
            </div>

            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px dashed rgba(255,255,255,0.2);">
                <p style="color: #fbbf24; font-size: 12px; margin-bottom: 5px;">⚠️ PASSO FINAL OBRIGATÓRIO</p>
                <p style="color: rgba(255,255,255,0.7); font-size: 12px; line-height: 1.4;">
                    Após pagar, envie o print do comprovante para:<br>
                    <strong style="color:white;">thi.macedo@gmail.com</strong><br>
                    <span style="font-size: 11px;">(Subject: Pagamento Sentinela - ${email})</span>
                </p>
            </div>

            <button onclick="location.reload()" style="background: transparent; border: none; color: rgba(255,255,255,0.5); cursor: pointer; margin-top: 20px; font-size: 13px;">
                Voltar ao painel
            </button>
        </div>
    `;
}

/*
// ==========================================
// CÓDIGO DO PIX GUARDADO PARA O FUTURO
// ==========================================
function renderPixModal(container, pixCode, email) {
    container.innerHTML = `
        <div style="text-align: center; padding: 10px;">
            <h2 style="color:white; font-size: 20px; margin-bottom: 10px;">Pagamento via PIX</h2>
            <p style="color: rgba(255,255,255,0.6); font-size: 13px; margin-bottom: 15px;">
                Valor: <strong style="color:#10b981; font-size:18px;">R$ ${PRECO_PLANO.toFixed(2)}</strong>
            </p>
            <div style="background: white; padding: 15px; border-radius: 12px; margin: 0 auto 15px; display:inline-block;">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(pixCode)}" alt="QR Code PIX">
            </div>
            <textarea id="pix-code-textarea" readonly style="width: 100%; height: 50px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: white; padding: 8px; font-size: 9px; resize: none;">${pixCode}</textarea>
            <button onclick="navigator.clipboard.writeText(document.getElementById('pix-code-textarea').value); this.innerText='✅ COPIADO!';" 
                style="width: 100%; margin-top: 10px; padding: 12px; background: #2563eb; color: white; font-weight: bold; border: none; border-radius: 8px; cursor: pointer;">
                📋 COPIAR CÓDIGO PIX
            </button>
            <button onclick="location.reload()" style="background: transparent; border: none; color: rgba(255,255,255,0.5); cursor: pointer; margin-top: 15px; font-size: 13px;">Voltar ao painel</button>
        </div>
    `;
}
*/

// Exposição global para chamadas via HTML onclick
window.initiatePayment = initiatePayment;
