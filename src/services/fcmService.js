// SENTINELA | Diamond Edition - FCM Service
// Gerencia notificações push via Firebase Cloud Messaging

import { dataService } from './dataService.js';
import { authService } from './authService.js';

class SentinelFCMService {
    constructor() {
        this.messaging = null;
        this.vapidKey = null;
    }

    async init() {
        console.log('[FCMService] Inicializando...');
        
        if (!('serviceWorker' in navigator)) {
            console.warn('[FCMService] Service Workers não suportados.');
            return;
        }

        try {
            // 1. Busca Configuração
            const config = await dataService.fetchJson('/config/firebase');
            if (!config || !config.apiKey) {
                console.warn('[FCMService] Configuração do Firebase incompleta.');
                return;
            }

            this.vapidKey = config.vapidKey;

            // 2. Carrega Firebase via Script dinâmico (compat para facilitar no SW)
            // No frontend principal usamos o módulo
            const { initializeApp } = await import('https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js');
            const { getMessaging, getToken, onMessage } = await import('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging.js');

            const app = initializeApp(config);
            this.messaging = getMessaging(app);

            // 3. Registra Service Worker
            const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
            console.log('[FCMService] Service Worker registrado com sucesso.');

            // 4. Solicita Permissão e Token
            await this.requestPermission();

            // 5. Listener para mensagens em foreground
            onMessage(this.messaging, (payload) => {
                console.log('[FCMService] Mensagem recebida em foreground:', payload);
                // Aqui poderíamos disparar um Toast na UI
                if (window.dispatchEvent) {
                    window.dispatchEvent(new CustomEvent('sentinela-notification', { detail: payload }));
                }
            });

        } catch (e) {
            console.error('[FCMService] Erro na inicialização:', e);
        }
    }

    async requestPermission() {
        try {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('[FCMService] Permissão concedida.');
                await this.saveToken();
            } else {
                console.warn('[FCMService] Permissão negada para notificações.');
            }
        } catch (e) {
            console.error('[FCMService] Erro ao solicitar permissão:', e);
        }
    }

    async saveToken() {
        if (!this.messaging || !authService.isAuthenticated()) return;

        try {
            const { getToken } = await import('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging.js');
            const currentToken = await getToken(this.messaging, {
                vapidKey: this.vapidKey,
                serviceWorkerRegistration: await navigator.serviceWorker.ready
            });

            if (currentToken) {
                console.log('[FCMService] Token obtido:', currentToken);
                
                // Registra no backend
                await fetch(`${window.SENTINELA_CONFIG.apiUrl}/auth/register-push-token`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: authService.user.id,
                        token: currentToken,
                        platform: 'web'
                    })
                });
                
                console.log('[FCMService] Token registrado no backend com sucesso.');
            } else {
                console.warn('[FCMService] Nenhum token disponível. Verifique as permissões.');
            }
        } catch (e) {
            console.error('[FCMService] Erro ao salvar token:', e);
        }
    }
}

export const fcmService = new SentinelFCMService();
