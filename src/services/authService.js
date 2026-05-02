// SENTINELA | Diamond Edition - Auth Service
// Gerencia autenticação e sessão real via Supabase Auth

const sbUrl = 'https://vhamejkldzxbeibqeqpk.supabase.co';
const sbKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY';

class SentinelAuthService {
    constructor() {
        if (typeof supabase === 'undefined') {
            console.error('[AuthService] Supabase SDK not loaded!');
            this.client = null;
            return;
        }
        this.client = supabase.createClient(sbUrl, sbKey);
        this.user = null;
        this.session = null;
    }

    async init() {
        if (!this.client) return null;

        const { data: { session } } = await this.client.auth.getSession();
        this.session = session;
        if (session) {
            this.user = await this.getProfile(session.user.id);
        }
        
        // Listener para mudanças de estado (Login/Logout)
        this.client.auth.onAuthStateChange(async (event, session) => {
            console.log(`[AuthService] Event: ${event}`);
            this.session = session;
            if (session) {
                this.user = await this.getProfile(session.user.id);
            } else {
                this.user = null;
            }
            if (window.forceRefresh) window.forceRefresh();
        });

        return this.user;
    }

    async getProfile(userId) {
        try {
            // Busca dados estendidos na tabela profiles (id, plan, username, stn_tokens)
            const { data, error } = await this.client
                .from('profiles')
                .select('*, stn_tokens')
                .eq('id', userId)
                .single();

            if (error) throw error;
            return data;
        } catch (e) {
            console.error('[AuthService] Error fetching profile:', e);
            // Fallback para dados básicos do Auth se o profile não existir
            return { id: userId, plan: 'public', username: 'Visitante', stn_tokens: 0 };
        }
    }

    async fetchUserTokens() {
        if (!this.session?.user) return 0;
        const profile = await this.getProfile(this.session.user.id);
        if (profile) {
            this.user = profile;
            if (window.forceRefresh) window.forceRefresh();
            return profile.stn_tokens || 0;
        }
        return 0;
    }


    async signIn(email, password) {
        if (!this.client) return;
        const { data, error } = await this.client.auth.signInWithPassword({ email, password });
        if (error) throw error;
        return data;
    }

    async signUp(email, password, username) {
        if (!this.client) return;
        const { data, error } = await this.client.auth.signUp({ 
            email, 
            password,
            options: { data: { username } }
        });
        if (error) throw error;
        return data;
    }

    async signOut() {
        if (!this.client) return;
        await this.client.auth.signOut();
        window.location.reload();
    }

    isAuthenticated() {
        return !!this.session;
    }

    getPlan() {
        return 'enterprise'; // Forçado para verificação total
    }
}

export const authService = new SentinelAuthService();
