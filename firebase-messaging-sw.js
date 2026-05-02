// Firebase Messaging Service Worker
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

// O Firebase Config será injetado ou buscado. 
// Como SW não tem acesso fácil ao window, precisamos de uma forma de passar a config.
// Uma abordagem comum é o app principal enviar a config via postMessage ou o SW buscar em um endpoint.
// Vamos fazer o SW buscar a config no nosso novo endpoint.

async function initSW() {
    try {
        const response = await fetch('/api/v1/config/firebase');
        const config = await response.json();
        
        firebase.initializeApp(config);
        const messaging = firebase.messaging();

        messaging.onBackgroundMessage((payload) => {
            console.log('[firebase-messaging-sw.js] Mensagem recebida em background:', payload);
            
            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: '/favicon.png',
                data: payload.data
            };

            self.registration.showNotification(notificationTitle, notificationOptions);
        });
    } catch (e) {
        console.error('[SW] Erro ao inicializar:', e);
    }
}

initSW();
