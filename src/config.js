// SENTINELA | Diamond Edition - Configuração Central v20.2.1
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = isLocalhost && window.location.port === '3000' 
    ? 'http://localhost:8000/api/v1' 
    : '/api/v1';

export const SENTINELA_CONFIG = {
    apiUrl: API_BASE,
    supabaseUrl: 'https://vhamejkldzxbeibqeqpk.supabase.co',
    supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY',
    refreshInterval: 3600000 
};

window.SENTINELA_CONFIG = SENTINELA_CONFIG;
