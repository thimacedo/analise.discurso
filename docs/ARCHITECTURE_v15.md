/**
 * SENTINELA — Documentação de Arquitetura v15.5
 * 
 * 1. Camada de Dados:
 *    - Supabase (PostgreSQL) como fonte única da verdade.
 *    - API Python (FastAPI) unificada no Vercel atuando como Middleware.
 * 
 * 2. Módulos Core:
 *    - app.js: Orquestrador de eventos e inicialização.
 *    - state.js: Gerenciador de estado centralizado (SSOT).
 *    - ui.js: Lógica de renderização e animações de interface.
 * 
 * 3. Protocolos de Segurança:
 *    - Admin: Protegido por TOTP (RFC 6238) validado no Backend.
 *    - API: Cabeçalhos CORS restritos e autenticação via Bearer Token.
 * 
 * 4. Design System:
 *    - Estética Stealth: Fundo #020617, Glassmorphism, Plus Jakarta Sans.
 */
