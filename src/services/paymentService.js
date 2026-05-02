// SENTINELA | Diamond Edition - Payment Service v20.3
// Orquestra Stripe, PayPal e PIX

import { authService } from './authService.js';

const API_BASE = window.SENTINELA_CONFIG?.apiUrl || '/api/v1';

class SentinelPaymentService {
    /**
     * Inicia o fluxo de compra de munição forense (STN)
     * @param {string} method - 'stripe', 'paypal', 'pix'
     * @param {number} amount - Quantidade de STN
     */
    async purchaseSTN(method, stnAmount) {
        console.log(`[Payments] Iniciando compra de ${stnAmount} STN via ${method}...`);
        
        try {
            const response = await fetch(`${API_BASE}/payments/create-order`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    method,
                    amount: stnAmount,
                    userId: authService.user?.id
                })
            });

            const order = await response.json();

            if (method === 'stripe') {
                window.location.href = order.checkoutUrl;
            } else if (method === 'pix') {
                return order.qrCode; // Retorna para o modal da UI
            } else if (method === 'paypal') {
                window.location.href = order.approvalUrl;
            }
        } catch (e) {
            console.error('[Payments] Erro no checkout:', e);
            throw e;
        }
    }

    async subscribePro() {
        // Fluxo específico para assinatura mensal via Stripe
        return this.purchaseSTN('stripe', 'subscription_pro');
    }
}

export const paymentService = new SentinelPaymentService();
