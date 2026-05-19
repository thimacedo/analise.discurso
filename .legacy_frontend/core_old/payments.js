// /src/core/payments.js
import { authService } from '../services/authService.js';

export async function initiateStripeCheckout(packageSlug) {
    const user = authService.user;
    if (!user) {
        alert("Necessário login para adquirir tokens de munição forense.");
        // Opcional: Abrir modal de login
        return;
    }

    // Configuração dos pacotes conforme o backend
    const PRICE_IDS = {
        'stn_starter': window.SENTINELA_CONFIG?.stripeStarterPriceId || 'price_1Starter',
        'stn_squad':   window.SENTINELA_CONFIG?.stripeSquadPriceId || 'price_1Squad',
        'stn_warroom': window.SENTINELA_CONFIG?.stripeWarroomPriceId || 'price_1WarRoom'
    };

    const priceId = PRICE_IDS[packageSlug];

    try {
        const resp = await fetch('/api/v1/checkout/create-session', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authService.session?.access_token}`
            },
            body: JSON.stringify({ 
                user_id: user.id, 
                package_slug: packageSlug,
                price_id: priceId
            })
        });
        
        if (!resp.ok) throw new Error('Falha ao gerar sessão de checkout');
        
        const { url } = await resp.json();
        if (url) {
            window.location.href = url;
        }
    } catch (e) {
        console.error('[Payments] Checkout error:', e);
        alert('Erro ao processar pagamento. Tente novamente mais tarde.');
    }
}

// Exposição global para chamadas via HTML onclick
window.initiateStripeCheckout = initiateStripeCheckout;
