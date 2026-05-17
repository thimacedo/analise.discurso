/**
 * PASA v44.2 - Auth Service: Supabase Authentication Wrapper
 * Handles user authentication and session management
 */
import { getSupabase } from '../core/supabase.js';

class SentinelAuthService {
    constructor() {
        // Initialize Supabase client using global provider
        this.supabase = getSupabase();
        
        this.user = null;
        this.session = null;
        this.profile = null;
    }

    /**
     * Initialize authentication service
     * @returns {Promise<Object|null>} User profile or null
     */
    async init() {
        try {
            // Get current session
            const { data: { session } } = await this.supabase.auth.getSession();
            this.session = session;
            
            if (session) {
                // Get user profile
                this.user = await this.getProfile(session.user.id);
                
                // Fetch organizations
                await this.fetchOrganizations();
            }
            
            // Set up auth state change listener
            this.supabase.auth.onAuthStateChange(async (event, session) => {
                this.session = session;
                
                if (session) {
                    this.user = await this.getProfile(session.user.id);
                    await this.fetchOrganizations();
                    
                    // Only refresh on actual login (not initialization)
                    if (event === 'SIGNED_IN' && window.forceRefresh) {
                        window.forceRefresh();
                    }
                } else {
                    this.user = null;
                    this.profile = null;
                    
                    // Clear organization state
                    const { State } = await import('../core/state.js');
                    State.organizations = [];
                    State.currentOrganizationId = null;
                    
                    // Only refresh on actual logout (not initialization)
                    if (event === 'SIGNED_OUT' && window.forceRefresh) {
                        window.forceRefresh();
                    }
                }
            });
            
            return this.user;
        } catch (error) {
            console.error('Auth initialization failed:', error);
            return null;
        }
    }

    /**
     * Fetch user profile from database
     * @param {string} userId - User ID
     * @returns {Promise<Object>} User profile
     */
    async getProfile(userId) {
        try {
            const { data, error } = await this.supabase
                .from('profiles')
                .select('*, stn_tokens')
                .eq('id', userId)
                .single();
            
            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Failed to fetch profile:', error);
            // Fallback to basic auth user data
            return {
                id: userId,
                plan: 'public',
                username: 'Visitante',
                stn_tokens: 0
            };
        }
    }

    /**
     * Fetch user organizations
     */
    async fetchOrganizations() {
        if (!this.session?.user) return;
        
        try {
            const { data, error } = await this.supabase
                .from('organization_members')
                .select('role, organizations(*)')
                .eq('profile_id', this.session.user.id);
            
            if (error) throw error;
            
            const organizations = data.map(m => ({
                ...m.organizations,
                user_role: m.role
            }));
            
            // Update state
            const { State } = await import('../core/state.js');
            State.organizations = organizations;
            
            // Set default organization if none selected
            if (!State.currentOrganizationId && organizations.length > 0) {
                State.currentOrganizationId = organizations[0].id;
                localStorage.setItem('sentinela_org_id', organizations[0].id);
            }
        } catch (error) {
            console.error('Failed to fetch organizations:', error);
        }
    }

    /**
     * Get current user's STN tokens
     * @returns {number} STN token balance
     */
    async getSTNTokens() {
        if (!this.session?.user) return 0;
        
        try {
            const profile = await this.getProfile(this.session.user.id);
            return profile?.stn_tokens || 0;
        } catch (error) {
            console.error('Failed to get STN tokens:', error);
            return 0;
        }
    }

    /**
     * Sign in with email and password
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<Object>} Auth response
     */
    async signIn(email, password) {
        try {
            const { data, error } = await this.supabase.auth.signInWithPassword({
                email,
                password
            });
            
            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Sign in failed:', error);
            throw error;
        }
    }

    /**
     * Sign up with email and password
     * @param {string} email - User email
     * @param {string} password - User password
     * @param {string} username - Desired username
     * @returns {Promise<Object>} Auth response
     */
    async signUp(email, password, username) {
        try {
            const { data, error } = await this.supabase.auth.signUp({
                email,
                password,
                options: {
                    data: { username }
                }
            });
            
            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Sign up failed:', error);
            throw error;
        }
    }

    /**
     * Sign out current user
     */
    async signOut() {
        try {
            await this.supabase.auth.signOut();
            // Force reload to clear state
            if (window.forceRefresh) window.forceRefresh();
        } catch (error) {
            console.error('Sign out failed:', error);
            throw error;
        }
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} Authentication status
     */
    isAuthenticated() {
        return !!this.session;
    }

    /**
     * Get current user's plan
     * @returns {string} User subscription plan
     */
    getPlan() {
        return this.profile?.plan || this.user?.plan || 'public';
    }

    /**
     * Check if user can access a feature
     * @param {string} feature - Feature to check
     * @returns {boolean} Access permission
     */
    canAccess(feature) {
        const plan = this.getPlan();
        
        // Enterprise plan has access to everything
        if (plan === 'enterprise') return true;
        
        // Feature-specific access
        switch (feature) {
            case 'identities':
                return plan === 'pro' || plan === 'enterprise';
            case 'pdf_export':
                return false; // Always requires STN tokens
            case 'advanced_analytics':
                return plan === 'pro' || plan === 'enterprise';
            default:
                return true; // Basic access for all plans
        }
    }

    /**
     * Mask sensitive identity information
     * @param {string} name - Name to mask
     * @returns {string} Masked name
     */
    maskName(name) {
        return this.canAccess('identities') 
            ? name 
            : 'Agressor Oculto';
    }
}

// Singleton instance
export const authService = new SentinelAuthService();
